from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
from authentication.models import Profile
from django.db import IntegrityError


class MemberService:

    def add_member_to_chama(self,request):

        data = json.loads(request.body)
        print(data)
    
        name = data.get('name')
        email = data.get('email')
        id_number = data.get('id_number')
        phone = data.get('phone')
        role = data.get('role')
        group = data.get('group')
        
        group = Chama.objects.get(pk=int(group))
        role = Role.objects.get(name = str(role))
        
        # Strip the first digit and add '+254'
        phone = '+254' + phone[1:]
        
        user = User.objects.filter(username=id_number).first()
        print('This is the user:', user)
        
        try:
            if user:
                profile = Profile.objects.get(owner=user)
                
                new_member = ChamaMember.objects.create(
                name = user.first_name + ' ' + user.last_name,
                email=user.email,
                mobile = profile.phone,
                group = group,
                role = role,
                user=user,
                profile=profile.picture,
                member_id=id_number
                
                )
                member_name = new_member.name
            else:
                new_member = ChamaMember.objects.create(
                name = name,
                mobile = phone,
                email=email,
                group = group,
                role = role,
                member_id=id_number
                )
                member_name = new_member.name
        except IntegrityError:
            data = {
                'status':'failed',
                'message':'User with that ID number already exists in the chama'
            }
            return JsonResponse(data,status=400)
        data = {
            'status':'success',
            'message':'member added succesfully',
            'member': member_name
        }

        return JsonResponse(data,status=200)
    
    def audit_chama_members(self,chama_id):
        chama = Chama.objects.get(pk=chama_id)
        for member in chama.member.all():
            user = User.objects.filter(username=member.member_id).first()
            if user:
                member.user = user
                member.save()

    def remove_member_from_chama(self,member_id,chama):
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
        
        

