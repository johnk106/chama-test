from chamas.models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import json
from authentication.models import Profile
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal


class ContributionService:
    @staticmethod
    def create_contribution(request,chama_id):
        name = request.POST['name']
        amount = request.POST['amount']
        start_date = request.POST['start-date']
        description = request.POST['description']
        # Grace period and end date are no longer used in the logic but may still be sent from UI
        # We ignore them by not extracting them from the request

        try:
            chama = Chama.objects.get(pk=chama_id)
            # Check for duplicate contribution name within the same chama, not globally
            contribution = Contribution.objects.filter(name=name, chama=chama).first()

            if contribution:
                data = {
                    'status':'failed',
                    'message':'A contribution with that name already exists in this chama, please choose another name'
                }

                return JsonResponse(data,status=409)
            if chama:
                 try:
                    new_contribution = Contribution.objects.create(
                name=name,
                amount=amount,
                description=description,
                chama = chama,
                start_date=start_date

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
            
            # Check if this is the new format (multiple contributions)
            if 'contribution_id' in data and 'contributions' in data:
                # Handle multiple contributions format
                contribution_id = data.get('contribution_id')
                contributions_list = data.get('contributions', [])
                
                if not contribution_id:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Contribution ID is required'
                    }, status=400)
                
                if not contributions_list:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'At least one contribution entry is required'
                    }, status=400)
                
                try:
                    contribution = Contribution.objects.get(pk=contribution_id)
                except Contribution.DoesNotExist:
                    return JsonResponse({
                        'status': 'failed',
                        'message': 'Contribution not found'
                    }, status=404)
                
                created_records = []
                errors = []
                
                for contrib_data in contributions_list:
                    try:
                        member_id = contrib_data.get('member_id')
                        amount = Decimal(str(contrib_data.get('amount', 0)))
                        
                        if amount <= 0:
                            errors.append(f'Invalid amount for member ID {member_id}')
                            continue
                            
                        try:
                            member = ChamaMember.objects.get(pk=member_id)
                        except ChamaMember.DoesNotExist:
                            errors.append(f'Member with ID {member_id} not found')
                            continue
                        
                        date = timezone.now()
                        amount_expected = contribution.amount
                        balance = amount_expected - amount
                        
                        # Create the main contribution record
                        new_contribution_record = ContributionRecord.objects.create(
                            contribution=contribution,
                            date_created=date,
                            amount_expected=amount_expected,
                            amount_paid=amount,
                            balance=balance if balance > 0 else Decimal('0.00'),
                            member=member,
                            chama=chama
                        )
                        
                        # Create cashflow record
                        CashflowReport.objects.create(
                            object_date=new_contribution_record.date_created,
                            member=new_contribution_record.member,
                            type='contribution',
                            amount=new_contribution_record.amount_paid,
                            chama=chama,
                            forGroup=False
                        )
                        
                        # If overpayment, create an additional record for the excess
                        if balance < 0:  # Overpayment
                            excess_amount = abs(balance)
                            ContributionRecord.objects.create(
                                contribution=contribution,
                                date_created=date,
                                amount_expected=Decimal('0.00'),
                                amount_paid=excess_amount,
                                balance=Decimal('0.00'),
                                member=member,
                                chama=chama
                            )
                        
                        created_records.append({
                            'id': new_contribution_record.id,
                            'member': member.name,
                            'amount_paid': float(amount),
                            'amount_expected': float(amount_expected),
                            'balance': float(new_contribution_record.balance),
                            'date_created': date.strftime('%Y-%m-%d')
                        })
                        
                    except (ValueError, TypeError) as e:
                        errors.append(f'Invalid amount for member ID {member_id}: {str(e)}')
                        continue
                    except Exception as e:
                        errors.append(f'Error processing member ID {member_id}: {str(e)}')
                        continue
                
                if created_records:
                    message = f'Successfully created {len(created_records)} contribution record(s)'
                    if errors:
                        message += f'. {len(errors)} error(s) occurred: {"; ".join(errors[:3])}'
                        if len(errors) > 3:
                            message += f' and {len(errors) - 3} more...'
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': message,
                        'records': created_records,
                        'errors': errors
                    }, status=200)
                else:
                    return JsonResponse({
                        'status': 'failed',
                        'message': f'No records created. Errors: {"; ".join(errors)}',
                        'errors': errors
                    }, status=400)
            
            else:
                # Handle legacy single contribution format
                contribution = Contribution.objects.get(pk=data.get('contribution'))
                date = timezone.now()
                amount_expected = contribution.amount
                amount_paid = Decimal(str(data.get('amount', 0)))
                member = ChamaMember.objects.get(pk=data.get('member'))

                # Validate amount
                if amount_paid < 0:
                    data = {
                        'status': 'failed',
                        'message': f'Amount for member {member.name} cannot be negative.'
                    }
                    return JsonResponse(data, status=400)

                if amount_paid == 0:
                    data = {
                        'status': 'failed',
                        'message': f'Amount for member {member.name} must be greater than zero.'
                    }
                    return JsonResponse(data, status=400)

                # Calculate balance (negative means overpayment, positive means underpayment)
                balance = amount_expected - amount_paid

                # Create the main contribution record
                new_contribution_record = ContributionRecord.objects.create(
                    contribution=contribution,
                    date_created=date,
                    amount_expected=amount_expected,
                    amount_paid=amount_paid,
                    balance=balance if balance > 0 else Decimal('0.00'),
                    member=member,
                    chama=chama
                )

                # Create cashflow record
                new_cashflow_object = CashflowReport.objects.create(
                    object_date=new_contribution_record.date_created,
                    member=new_contribution_record.member,
                    type='contribution',
                    amount=new_contribution_record.amount_paid,
                    chama=chama,
                    forGroup=False
                )

                # If overpayment, create an additional record for the excess
                if balance < 0:  # Overpayment
                    excess_amount = abs(balance)
                    ContributionRecord.objects.create(
                        contribution=contribution,
                        date_created=date,
                        amount_expected=Decimal('0.00'),  # No expectation for excess
                        amount_paid=excess_amount,
                        balance=Decimal('0.00'),  # Excess has no balance
                        member=member,
                        chama=chama
                    )

                data = {
                    'status': 'success',
                    'message': f'Contribution record created successfully for {member.name}',
                    'record': {
                        'id': new_contribution_record.id,
                        'member': member.name,
                        'amount_paid': float(amount_paid),
                        'amount_expected': float(amount_expected),
                        'balance': float(new_contribution_record.balance),
                        'date_created': date.strftime('%Y-%m-%d')
                    }
                }
                return JsonResponse(data, status=200)
                
        except Contribution.DoesNotExist:
            data = {
                'status': 'failed',
                'message': 'Contribution not found'
            }
            return JsonResponse(data, status=404)
        except ChamaMember.DoesNotExist:
            data = {
                'status': 'failed',
                'message': 'Member not found'
            }
            return JsonResponse(data, status=404)
        except (ValueError, TypeError) as e:
            data = {
                'status': 'failed',
                'message': f'Invalid amount provided: {str(e)}'
            }
            return JsonResponse(data, status=400)
        except Exception as e:
            print(f"Error in create_contribution_record: {e}")
            data = {
                'status': 'failed',
                'message': f'An error occurred during record creation: {str(e)}'
            }
            return JsonResponse(data, status=500)
        
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

    



