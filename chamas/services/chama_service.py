from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json


class ChamaService:
    @staticmethod
    def create_chama_type(request):
        name = request.POST['name']

        try:
            new_type = ChamaType.objects.create(name=name)
            data = {
                'status':'success',
                'message':'chama type created succesfully',
                'type':model_to_dict(new_type)

            }
            return JsonResponse(data,status=200)
        except Exception as e:
            data = {
                'status':'failed',
                'message':f'an error occured:{e}'

            }
            return JsonResponse(data,status=400)
        
    @staticmethod
    def create_chama(request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            start = data.get('date')
            type = data.get('type')
            created_by = request.user
           

            _type = ChamaType.objects.get(pk=int(type))

            new_chama = Chama.objects.create(
                name=name,
                type = _type,
                created_by = created_by,
                start_date=start
            )

            name = f'{created_by.first_name} {created_by.last_name}'
            role = Role.objects.filter(name='admin').first()

            new_chama_member = ChamaMember.objects.create(
                name = name,
                email=created_by.email,
                mobile = created_by.profile.phone,
                group = new_chama,
                role = role,
                user=created_by
            )

            data = {
                'status':'success',
                'message':'Chama created succesfully',
                'chama':model_to_dict(new_chama)
            }
            return JsonResponse(data,status = 200,)
        
        except Exception as e:
            print(e.args)
            data = {
                'status':'failed',
                'message':f'An error occured: {e}'
            }
            return JsonResponse(data,status=200)
       


