from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
from authentication.models import Profile
from django.db import IntegrityError


class MemberService:
    @staticmethod
    def add_member_to_chama(request):
        try:
            data = json.loads(request.body)
            print(f"[DEBUG] Adding member with data: {data}")
        
            name = data.get('name')
            email = data.get('email')
            mobile = data.get('mobile')  # Changed from phone to mobile to match frontend
            role_id = data.get('role')
            group_id = data.get('group') or data.get('chama_id')
            id_number = data.get('id_number') or data.get('member_id')
            
            # Validate required fields
            if not all([name, email, mobile, role_id, group_id]):
                return JsonResponse({
                    'status': 'failed',
                    'message': 'Missing required fields'
                }, status=400)
            
            group = Chama.objects.get(pk=int(group_id))
            role = Role.objects.get(pk=int(role_id))
            
            # Format phone number if needed
            if mobile and not mobile.startswith('+'):
                if mobile.startswith('0'):
                    mobile = '+254' + mobile[1:]
                elif mobile.startswith('254'):
                    mobile = '+' + mobile
                else:
                    mobile = '+254' + mobile
            
            # Check if user exists by ID number or email
            user = None
            if id_number:
                user = User.objects.filter(username=id_number).first()
            if not user:
                user = User.objects.filter(email=email).first()
            
            print(f'[DEBUG] Found existing user: {user}')
            
            # Create member
            if user:
                try:
                    profile = Profile.objects.get(owner=user)
                    profile_picture = profile.picture
                    actual_mobile = profile.phone or mobile
                except Profile.DoesNotExist:
                    profile_picture = None
                    actual_mobile = mobile
                
                new_member = ChamaMember.objects.create(
                    name=user.first_name + ' ' + user.last_name if user.first_name else name,
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
                'message': f'{new_member.name} added successfully to chama',
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
    def remove_member_from_chama(member_id,chama):
        try:
            chama_member = ChamaMember.objects.get(group=chama, id=member_id)
            if chama_member.user == chama.created_by:
                data = {
                    'status':'failed',
                    'message':'Sorry you can not remove a group creator!'
                        }
                return JsonResponse(data,status=200)
            try:
                chama_member.active = False
                chama_member.save()
            except Exception as e:
                print(e)
            data = {
                'status':'success',
                'message':'User succesfully removed from chama',
                'member_id':member_id
            }
            return JsonResponse(data,status=200)
        except ChamaMember.DoesNotExist:
            data = {
                'status':'failed',
                'message':'Member is not group of this chama'
            }
            return JsonResponse(data,status=400)
        
        

