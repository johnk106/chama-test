from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
from authentication.models import Profile
from django.db import IntegrityError
from django.core.paginator import Paginator


class ContributionService:
    @staticmethod
    def create_contribution(request,chama_id):
        name = request.POST['name']
        amount = request.POST['amount']
        start_date = request.POST['start-date']
        grace_period = request.POST['grace-period']
        description = request.POST['description']
        end_date = request.POST['end-date']

        try:
            chama = Chama.objects.get(pk=chama_id)
            contribution = Contribution.objects.filter(name=name).first()

            if contribution:
                data = {
                    'status':'failed',
                    'message':'A contribution with that id already exists,please choose another name'
                }

                return JsonResponse(data,status=409)
            if chama:
                 try:
                    new_contribution = Contribution.objects.create(
                name=name,
                amount=amount,
                grace_period=grace_period,
                description=description,
                chama = chama,
                start_date=start_date,
                end_date=end_date

                    )

                    data = {
                'status':'success',
                'message':'Contribution created succesfully.',
                'contribution':model_to_dict(new_contribution)
                    }
                    return JsonResponse(data,status=200)
                 except Exception as e:
                     data = {
                         'status':'Failed',
                         'message':f'An error accured {e}'
                     }
                     print(e)
                     return JsonResponse(data,status=400)
            else:
                data = {
                    'status':'failed',
                    'message':'Chama with that id could not be found'
                }
                return JsonResponse(data,status=404)
        except Exception as e:
            print(e)
            data = {
                'status':'success',
                'message':f'an error accurred:{e}'
            }
            return JsonResponse(data,status=400)

    @staticmethod
    def create_contribution_record(request,chama_id):
        try:
            chama = Chama.objects.get(pk=chama_id)

            data = json.loads(request.body)
            contribution = Contribution.objects.get(pk=data.get('contribution'))
            date = timezone.now()
            amount_expected = contribution.amount
            amount_paid = Decimal(data.get('amount'))
            member = ChamaMember.objects.get(pk=data.get('member'))

            # Calculate balance
            balance = amount_paid - amount_expected

            if amount_paid < 0 or amount_paid is None:
                data = {
                    'status': 'failed',
                    'message': f'Amount for member {member.name} is either negative or has not been passed.'
                }
                return JsonResponse(data, status=200)

            # If amount paid is greater than the contribution amount
            if amount_paid > amount_expected:
                # Create contribution record with balance carried forward
                new_contribution_record = ContributionRecord.objects.create(
                    contribution=contribution,
                    date_created=date,
                    amount_expected=amount_expected,
                    amount_paid=amount_expected,  # Set amount paid to the expected amount
                    balance=0,  # No balance remaining for this contribution
                    member=member,
                    chama = chama
                )

                # Calculate the extra amount
                extra_amount = amount_paid - amount_expected

                # Create a contribution record for the extra amount with the next due date
                
                ContributionRecord.objects.create(
                        contribution=contribution,
                        date_created=timezone.now(),
                        amount_expected=amount_expected,  # No expected amount for extra contribution
                        amount_paid=extra_amount,
                        balance=amount_expected - extra_amount,  # No balance for extra contribution
                        member=member,
                        chama=chama
                    )

            else:
                # Create contribution record with no balance carried forward
                new_contribution_record = ContributionRecord.objects.create(
                    contribution=contribution,
                    date_created=date,
                    amount_expected=amount_expected,
                    amount_paid=amount_paid,
                    balance=abs(balance),
                    member=member,
                    chama=chama
                )

            new_cashflow_object = CashflowReport.objects.create(
                object_date=new_contribution_record.date_created,
                member=new_contribution_record.member,
                type='contribution',
                amount=new_contribution_record.amount_paid,
                chama=chama,
                forGroup=False
            )

            data = {
                'status': 'success',
                'message': f'Contribution record created successfully for {member.name}',
                'record': model_to_dict(new_contribution_record)
            }

            return JsonResponse(data, status=200)
        except Exception as e:
            print(e)
            data = {
                'status': 'failed',
                'message': f'An error occurred during record creation: {e}'
            }

            return JsonResponse(data, status=200)
        
    @staticmethod
    def pay_contribution(request,contribution_id):
        try:
            contribution = ContributionRecord.objects.get(pk=contribution_id)

            data = json.loads(request.body)
            amount = Decimal(data.get('amount'))

            if contribution.balance <= Decimal('0.00'):
                data = {
                    'status': 'failed',
                    'message': 'This contribution does not have a balance'
                }
                return JsonResponse(data, status=200)
            else:
                # Calculate remaining balance after payment
                remaining_balance = contribution.balance - amount

                if remaining_balance >= Decimal('0.00'):
                    # Update the contribution record with the payment and new balance
                    contribution.amount_paid += amount
                    contribution.balance = remaining_balance
                    contribution.save()
                else:
                    # Create a new contribution record for the extra amount with the next due date
                    extra_amount = abs(remaining_balance)
                    next_due_date = contribution.contribution.calculate_next_due_date()
                    if next_due_date:
                        ContributionRecord.objects.create(
                            contribution=contribution.contribution,
                            date_created=next_due_date,
                            amount_expected=0,  # No expected amount for extra contribution
                            amount_paid=extra_amount,
                            balance=0,  # No balance for extra contribution
                            member=contribution.member
                        )

                    # Update the current contribution record with the full balance paid
                    contribution.amount_paid += (amount - extra_amount)
                    contribution.balance = 0
                    contribution.save()

                cashflow = CashflowReport.objects.create(
                    object_date = timezone.now(),
                    member = contribution.member,
                    type = 'contribution balance payment',
                    chama = contribution.contribution.chama,
                    amount = Decimal(amount),
                    forGroup=False
                )

                data = {
                    'status': 'success',
                    'message': 'Contribution payment processed successfully'
                }
                return JsonResponse(data, status=200)
        except ContributionRecord.DoesNotExist:
            data = {
                'status': 'failed',
                'message': 'Contribution record does not exist'
            }
            return JsonResponse(data, status=404)
        except Exception as e:
            data = {
                'status': 'failed',
                'message': f'An error occurred during payment: {str(e)}'
            }
            return JsonResponse(data, status=500)
        
    @staticmethod
    def contribution_details(request,chama_id):
        data = json.loads(request.body)
        name = data.get('name')
        chama = Chama.objects.get(pk=chama_id)

        try:
            contribution = Contribution.objects.get(name=name, chama=chama)
            _records = Paginator(ContributionRecord.objects.filter(contribution=contribution).order_by('-date_created').all(),(chama.member.count()*5))
            records_page = _records.page(1)

            data = {
                'status': 'success',
                'message': 'contribution retrieved successfully',
                'contribution': model_to_dict(contribution, fields=['name', 'id', 'amount']),  # Adjust fields as needed
                'records': ContributionService.serialize_paginated_records(records_page),
            }

            return JsonResponse(data, status=200)

        except Contribution.DoesNotExist:
            data = {
                'status': 'error',
                'message': f'Contribution with name "{name}" not found in Chama {chama_id}',
            }
            return JsonResponse(data, status=404)

        except Exception as e:
            print(e)
            data = {
                'status': 'error',
                'message': f'An error occurred: {e}',
            }
            return JsonResponse(data, status=500)
        
    @staticmethod
    def serialize_paginated_records(records_page):
        serialized_records = [model_to_dict(record) for record in records_page]
        for record in serialized_records:
            member = ChamaMember.objects.get(pk=record['member'])
            record['member'] = member.name
            contribution = Contribution.objects.get(pk=record['contribution'])
            record['contribution'] = contribution.name
            record['date_created']  = record['date_created'].strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'page': records_page.number,
            'total_pages': records_page.paginator.num_pages,
            'total_records': records_page.paginator.count,
            'results': serialized_records,
    }

    



