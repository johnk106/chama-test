from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
from authentication.models import Profile
from django.db import IntegrityError
from django.db import models


class MemberService:
    @staticmethod
    def add_member_to_chama(request):
        try:
            print(f"[DEBUG] Request body: {request.body}")
            print(f"[DEBUG] Request content type: {request.content_type}")
            
            if not request.body:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Empty request body'
                }, status=400)
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON decode error: {str(e)}")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Invalid JSON data: {str(e)}'
                }, status=400)
                
            print(f"[DEBUG] Parsed data: {data}")
            print(f"[DEBUG] Data keys: {list(data.keys())}")
            print(f"[DEBUG] Data type: {type(data)}")
        
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            mobile = data.get('mobile', '').strip()
            role_id = data.get('role')
            group_id = data.get('group') or data.get('chama_id')
            id_number = data.get('id_number') or data.get('member_id')
            
            print(f"[DEBUG] Extracted values - name: '{name}', email: '{email}', mobile: '{mobile}', role_id: '{role_id}', group_id: '{group_id}'")
            
            # Validate required fields
            if not all([name, email, mobile, role_id, group_id]):
                missing_fields = []
                if not name: missing_fields.append('name')
                if not email: missing_fields.append('email')
                if not mobile: missing_fields.append('mobile')
                if not role_id: missing_fields.append('role')
                if not group_id: missing_fields.append('chama_id')
                
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Please enter a valid email address'
                }, status=400)
            
            try:
                group = Chama.objects.get(pk=int(group_id))
                print(f"[DEBUG] Found chama: {group.name}")
            except Chama.DoesNotExist:
                print(f"[ERROR] Chama with ID {group_id} not found")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Chama with ID {group_id} not found'
                }, status=400)
            except ValueError as e:
                print(f"[ERROR] Invalid chama ID: {group_id}")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Invalid chama ID: {group_id}'
                }, status=400)
            
            try:
                role = Role.objects.get(pk=int(role_id))
                print(f"[DEBUG] Found role: {role.name}")
            except Role.DoesNotExist:
                print(f"[ERROR] Role with ID {role_id} not found")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Role with ID {role_id} not found'
                }, status=400)
            except ValueError as e:
                print(f"[ERROR] Invalid role ID: {role_id}")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Invalid role ID: {role_id}'
                }, status=400)
            
            # Format phone number if needed
            if mobile and not mobile.startswith('+'):
                if mobile.startswith('0'):
                    mobile = '+254' + mobile[1:]
                elif mobile.startswith('254'):
                    mobile = '+' + mobile
                else:
                    mobile = '+254' + mobile
            
            # Check for existing member with same email or mobile in this chama
            existing_member = ChamaMember.objects.filter(
                group=group,
                active=True
            ).filter(
                models.Q(email__iexact=email) | models.Q(mobile=mobile)
            ).first()
            
            if existing_member:
                return JsonResponse({
                    'status': 'failed',
                    'message': 'A member with this email or phone number already exists in this chama'
                }, status=400)
            
            # Check if user exists by ID number or email
            user = None
            if id_number:
                user = User.objects.filter(username=id_number).first()
            if not user:
                user = User.objects.filter(email__iexact=email).first()
            
            print(f'[DEBUG] Found existing user: {user}')
            
            # Create member
            if user:
                try:
                    profile = Profile.objects.get(owner=user)
                    profile_picture = profile.picture
                    actual_mobile = profile.phone or mobile
                    actual_name = f"{user.first_name} {user.last_name}".strip() if user.first_name else name
                except Profile.DoesNotExist:
                    profile_picture = None
                    actual_mobile = mobile
                    actual_name = f"{user.first_name} {user.last_name}".strip() if user.first_name else name
                
                new_member = ChamaMember.objects.create(
                    name=actual_name,
                    email=user.email,
                    mobile=actual_mobile,
                    group=group,
                    role=role,
                    user=user,
                    profile=profile_picture,
                    member_id=id_number or user.username
                )
            else:
                new_member = ChamaMember.objects.create(
                    name=name,
                    mobile=mobile,
                    email=email,
                    group=group,
                    role=role,
                    member_id=id_number
                )
            
            print(f"[DEBUG] Successfully created member: {new_member.name}")
            
            # Return member data for frontend
            member_data = {
                'id': new_member.id,
                'name': new_member.name,
                'email': new_member.email,
                'mobile': new_member.mobile,
                'role': new_member.role.name,
                'member_since': new_member.member_since.strftime('%b %Y'),
                'profile': new_member.profile.url if new_member.profile else None
            }
            
            return JsonResponse({
                'status': 'success',
                'message': f'{new_member.name} added successfully to the chama',
                'member': member_data
            }, status=200)
            
        except IntegrityError as e:
            print(f"[ERROR] IntegrityError adding member: {str(e)}")
            return JsonResponse({
                'status': 'failed',
                'message': 'A member with this information already exists in the chama'
            }, status=400)
        except (Chama.DoesNotExist, Role.DoesNotExist) as e:
            print(f"[ERROR] Invalid chama or role: {str(e)}")
            return JsonResponse({
                'status': 'failed',
                'message': 'Invalid chama or role specified'
            }, status=400)
        except Exception as e:
            print(f"[ERROR] Unexpected error adding member: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'failed',
                'message': 'An error occurred while adding the member'
            }, status=500)
    
    @staticmethod
    def audit_chama_members(chama_id):
        chama = Chama.objects.get(pk=chama_id)
        for member in chama.member.all():
            user = User.objects.filter(username=member.member_id).first()
            if user:
                member.user = user
                member.save()
                
    @staticmethod
    def remove_member_from_chama(member_id, chama):
        print(f"[DEBUG] Attempting to remove member ID: {member_id} from chama: {chama.name}")
        
        try:
            chama_member = ChamaMember.objects.get(group=chama, id=member_id, active=True)
            print(f"[DEBUG] Found member: {chama_member.name} ({chama_member.email})")
            
            # Check if member is the chama creator
            if chama_member.user == chama.created_by:
                print(f"[WARNING] Attempt to remove chama creator: {chama_member.name}")
                return JsonResponse({
                    'status': 'failed',
                    'message': f'Cannot remove {chama_member.name} - they are the chama creator!'
                }, status=400)
            
            # Check if member has outstanding loans or contributions
            outstanding_loans = chama_member.loans.filter(balance__gt=0).count()
            if outstanding_loans > 0:
                print(f"[WARNING] Member {chama_member.name} has {outstanding_loans} outstanding loans")
                # You might want to add a warning but still allow removal
            
            try:
                # Soft delete - set member as inactive
                chama_member.active = False
                chama_member.save()
                print(f"[SUCCESS] Member {chama_member.name} marked as inactive")
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'{chama_member.name} has been successfully removed from {chama.name}',
                    'member_id': member_id,
                    'member_name': chama_member.name
                }, status=200)
                
            except Exception as e:
                print(f"[ERROR] Failed to deactivate member: {str(e)}")
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Failed to remove member due to a database error'
                }, status=500)
                
        except ChamaMember.DoesNotExist:
            print(f"[ERROR] Member with ID {member_id} not found in chama {chama.name}")
            return JsonResponse({
                'status': 'failed',
                'message': 'Member not found in this chama or already removed'
            }, status=404)
        except Exception as e:
            print(f"[ERROR] Unexpected error removing member: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': 'failed',
                'message': 'An unexpected error occurred while removing the member'
            }, status=500)
        
        

