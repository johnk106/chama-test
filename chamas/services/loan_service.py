from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
import uuid


class LoanService:

    def create_loan_type(self,request,chama_id):
        data =  json.loads(request.body)

        random_number = uuid.uuid4().int % 1000  
        type_id = f'LT{random_number:03d}' 
        name = data.get('name')
        max_loan_amount = data.get('max')
        grace_period = data.get('grace_period')

        max_due = data.get('max_due')
        late_fine = data.get('late_fine')
        intrest_rate = data.get('intrest_rate')
        description = data.get('description')
        schedule = data.get('schedule')


        try:
            chama = Chama.objects.get(pk=chama_id)
            new_type = LoanType.objects.create(
                
                type_id = type_id,
                name = name,
                max_loan_amount=max_loan_amount,
                grace_period=grace_period,
                late_fine=late_fine,
                intrest_rate=intrest_rate,
                description=description,
                chama= chama,
                max_due = max_due,
                schedule=schedule
            )
            

            data = {
                'status':'success',
                'message':'loan type created succesfully',
                'type':model_to_dict(new_type)
            }
            return JsonResponse(data,status=200)
        except Exception as e:
            data = {
                'status':'failed',
                'message':f'an error occurred:{e}'
            }
            print(2)
            return JsonResponse(data,status=200)
        
    def issue_loan(self,request,chama_id):
        chama = Chama.objects.get(pk=chama_id)

        data = json.loads(request.body)
        type = LoanType.objects.get(pk=data.get('type'))
        member = ChamaMember.objects.get(pk=data.get('member'))
        amount = int(data.get('amount'))
        schedule = type.schedule
        due = data.get('due')

        start_date_str = data.get('start_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        status = 'active'

        if type.schedule == 'weekly':
            end_date = start_date + relativedelta(weeks=int(due))
            
        elif type.schedule == 'monthly':
            end_date = start_date + relativedelta(weeks=int(due))
        
        if schedule == 'monthly':
            if type.schedule == 'weekly':
                weeks = int(due) * 4
                if weeks < int(due):
                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)
                
            elif type.max_due < int(due):
                data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                }
                return JsonResponse(data,status=200)


        elif schedule == 'weekly':
            if type.schedule == 'weekly':
                if type.max_due < int(due):
                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)
            elif type.schedule == 'monthly':
                weeks = type.max_due * 4
                if weeks < int(due):
                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)

        if(amount > type.max_loan_amount):
            data = {
                'status':'failed',
                'message':'The loan amount is greater than the maximum allowed for this loan'
            }
            return JsonResponse(data,status=406)

        new_loan = LoanItem.objects.create(
            member=member,
            amount=amount,
            intrest_rate=type.intrest_rate,  # Directly assign interest rate
            start_date=start_date,
            end_date=end_date,
            status=status,
            type=type,
            total_paid=Decimal('0.00'),
            chama=chama,
            due = due,
            schedule = schedule
        )
        new_loan.calc_tot_amount_to_be_paid()

        new_loan = model_to_dict(new_loan)
        new_loan['member'] = member.name
        new_loan['type'] = type.name

        data = {
            'status': 'success',
            'message': 'Loan issued successfully',
            'loan': new_loan
        }

        return JsonResponse(data, status=200)
    
    def apply_loan(self,request,chama_id):
        data = json.loads(request.body)

        loan_type = data.get('loan_type')
        loan = LoanType.objects.get(pk=loan_type)
        amount = int(data.get('amount'))
        due = data.get('due')
        schedule = loan.schedule
        chama = Chama.objects.get(pk=chama_id)

        if schedule == 'monthly':
            if loan.schedule == 'weekly':
                weeks = int(due) * 4
                if weeks < int(due):
                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)
            
            elif loan.max_due < int(due):
                data = {
                'status':'failed',
                'message':'the loan amount due is longer than the allowed period for this loan'
                }
                return JsonResponse(data,status=200)


        elif schedule == 'weekly':
            if loan.schedule == 'weekly':
                if loan.max_due < int(due):

                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)
            elif loan.schedule == 'monthly':
                weeks = loan.max_due * 4
                if weeks < int(due):
                    data = {
                    'status':'failed',
                    'message':'the loan amount due is longer than the allowed period for this loan'
                    }
                    return JsonResponse(data,status=200)

        


        if(amount > loan.max_loan_amount):
            data = {
                'status':'failed',
                'message':'The loan amount or repayment term is greater than the maximum allowed'
            }
            return JsonResponse(data,status=406)


        for member in chama.member.all():
            if member.user == request.user:
                member = member
                break

        try:
            new_application = LoanItem.objects.create(
                member=member,
                amount = amount,
                type=loan,
                chama=chama,
                due = due,
                schedule=schedule
            )
            data = {
                'status':'success',
                'message':'Loan request submitted succesfully',
                'application':model_to_dict(new_application)
            }
            return JsonResponse(data,status=200)

        except Exception as e:
            data = {
                'status':'failed',
                'message':f'an error happened:{e}'
            }
            return JsonResponse(data,status=200)
        
    def accept_loan_request(self,request,chama_id,loan_id):
        loan = LoanItem.objects.get(pk=loan_id)

        loan.status = 'active'
        loan.intrest_rate = loan.type.intrest_rate
        loan.start_date = timezone.now()
        if loan.schedule == 'monthly':
            loan.end_date = timezone.now() + relativedelta(months=loan.due)
        elif loan.schedule == 'weekly':
            loan.end_date = timezone.now() + relativedelta(weeks=loan.due)
        
        loan.total_paid = 0.00
        loan.last_updated = timezone.now()
        loan.calc_tot_amount_to_be_paid()
        loan.save()

        new_cashflow_object = CashflowReport.objects.create(
            object_date=loan.start_date,
            member=loan.member,
            type='loan disbursment',
            amount=loan.amount,
            chama=loan.chama,
            forGroup=False
        )

        data = {
            'status': 'success',
            'message': 'Loan approved successfully',
            'loan': model_to_dict(loan)
        }
        return JsonResponse(data, status=200)
    
    def decline_loan(self,loan_id):
        loan = LoanItem.objects.get(pk=loan_id)
        loan.status = 'declined'
        loan.last_updated = timezone.now()

        loan.save()

        data = {
            'status':'success',
            'message':'loan declined succesfully'

        }
        return JsonResponse(data,status = 200)
    
    def update_loan(self,request,loan):
        data = json.loads(request.body)

        loan_amount = data.get('loan_amount')

        if loan.status == 'active':
            loan.balance -= int(loan_amount)
            loan.total_paid += int(loan_amount)  # Add interest to total paid
            loan.last_updated = timezone.now()
            loan.save()

            if loan.balance <= Decimal('0.00'):
                loan.status = 'cleared'
                loan.save()

            new_cashflow_object = CashflowReport.objects.create(
                object_date=loan.start_date,
                type='loan payment',
                amount=Decimal(loan_amount),
                chama=loan.chama,
                forGroup=False,
                member=loan.member,
            )
        else:
            pass

        data = {
            'status': 'success',
            'message': 'Loan updated successfully',
            'loan': model_to_dict(loan)
        }

        return JsonResponse(data, status=200)




