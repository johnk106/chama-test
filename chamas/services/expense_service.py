from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
import uuid


class ExpenseService:
    @staticmethod
    def create_expense(request,chama):
        data = json.loads(request.body)

        name = data.get('name')
        amount = data.get('amount')
        description = data.get('description')

        for member in chama.member.all():
            if member.user == request.user:
                member = member
                print(member)

        try:
            new_expense = Expense.objects.create(
                name=name,
                amount=amount,
                description=description,
                chama=chama,
                created_by=member
                )
            
            new_cashflow_object = CashflowReport.objects.create(
                        object_date = new_expense.created_on,
                        type = 'expense',
                        amount = new_expense.amount,
                        chama = chama,
                        forGroup = True
                    )
            
            data = {
                'status':'success',
                'message':'expense created succesfully',
                'expense':model_to_dict(new_expense)
            }

            return JsonResponse(data,status=200)

        except Exception as e:

            data = {
               'status':'failed',
               'message':f'an error occurred:{e}' 
            }
            return JsonResponse(data,status=200)

