import json
import uuid
from django.db import IntegrityError
from django.shortcuts import render,get_object_or_404

from chamas.decorators import is_user_chama_member
from .models import *
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta,datetime
from django.db.models import Sum
import calendar
from django.http import FileResponse
import os
import csv
from authentication.models import Profile
from dateutil.relativedelta import relativedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.platypus             import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Table, TableStyle, Spacer
)
# import logging
# logger = logging.getLogger(__name__)



# Create your views here.
def get_user_role(request):
    group_id = request.GET.get('group_id')
    chama_member = ChamaMember.objects.get(user=request.user, group_id=group_id)
    return JsonResponse({'role': chama_member.role.name})


@login_required(login_url='/user/Login')
@is_user_chama_member
def dashboard(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)

    total_contributions = ContributionRecord.objects.filter(member__group=chama).aggregate(total_contributions=Sum('amount_paid'))['total_contributions'] or 0
    total_savings = Saving.objects.filter(chama=chama).aggregate(total_savings=Sum('amount'))['total_savings'] or 0
    total_fines = FineItem.objects.filter(member__group=chama).aggregate(total_fines=Sum('fine_amount'))['total_fines'] or 0
    total_loans_issued = LoanItem.objects.filter(member__group=chama).exclude(status__in=['declined', 'application']).aggregate(total_loans_issued=Sum('amount'))['total_loans_issued'] or 0
    contributions_data, loans_data, fines_data = get_monthly_data(chama_id)
    documents = Paginator(Document.objects.filter(chama=chama).order_by('-upload_date').all(),4)
    documents = documents.page(1)

    # Convert Decimal values to float
    contributions_data_float = {k: float(v) for k, v in contributions_data.items()}
    loans_data_float = {k: float(v) for k, v in loans_data.items()}
    fines_data_float = {k: float(v) for k, v in fines_data.items()}

    # Serialize dictionaries to JSON format
    contributions_data_json = json.dumps(contributions_data_float)
    loans_data_json = json.dumps(loans_data_float)
    fines_data_json = json.dumps(fines_data_float)

    remaining_count = max(chama.member.count() - 5, 0)

    notifications = Paginator(NotificationItem.objects.filter(forGroup=True,chama=chama).order_by('-date'),3).page(1)
    member = None
    for member in chama.member.all():
        if member.user == request.user:
            member = member
            break
    my_notifications = Paginator(NotificationItem.objects.filter(forGroup=False,chama=chama,member=member).order_by('-date'),3).page(1)

    return render(request,
                  'chamas/dashboard.html',
                  {'chama': chama, 
                    'total_contributions': total_contributions, 
                    'total_savings': total_savings, 
                    'total_fines': total_fines, 
                    'total_loans': total_loans_issued, 
                    'documents':documents,
                    'contributions_data': contributions_data_json, 
                   'loans_data': loans_data_json, 
                   'fines_data': fines_data_json,
                   'remaining_count': remaining_count,
                   'notifications':notifications,
                   'my_notifications':my_notifications
                    })

def get_monthly_data(chama_id):
    # Get the current year
    current_year = timezone.now().year

    # Initialize dictionaries to store monthly data
    contributions_data = {}
    loans_data = {}
    fines_data = {}

    # Loop through each month
    for month in range(1, 13):
        # Get the name of the month
        month_name = calendar.month_abbr[month]

        # Get total contributions for the month
        total_contributions = ContributionRecord.objects.filter(
            date_created__year=current_year, date_created__month=month, member__group__id=chama_id
        ).aggregate(total_contributions=Sum('amount_paid'))['total_contributions'] or 0
        contributions_data[month_name] = total_contributions

        # Get total loans for the month
        total_loans = LoanItem.objects.filter(
            applied_on__year=current_year, applied_on__month=month, member__group__id=chama_id
        ).exclude(status__in=['declined', 'application']).aggregate(total_loans=Sum('amount'))['total_loans'] or 0
        loans_data[month_name] = total_loans

        # Get total fines for the month
        total_fines = FineItem.objects.filter(
            created__year=current_year, created__month=month, member__group__id=chama_id
        ).aggregate(total_fines=Sum('fine_amount'))['total_fines'] or 0
        fines_data[month_name] = total_fines

    return contributions_data, loans_data, fines_data

@login_required(login_url='/user/Login')
def upload_document(request, chama_id):
    if request.method == 'POST' and request.FILES.get('documentFile'):
        document = request.FILES['documentFile']
        name = document.name
        try:
            chama = Chama.objects.get(pk=chama_id)
        except Chama.DoesNotExist:
            return JsonResponse({'error': 'Chama not found'}, status=404)

        new_document = Document.objects.create(file=document, name=name, chama=chama)

        return JsonResponse({'message': 'Document uploaded successfully'}, status=200)
    else:
        return JsonResponse({'error': 'No document provided'}, status=400)

@login_required(login_url='/user/Login')
def download_document(request, document_id,chama_id):
    chama = Chama.objects.get(pk=chama_id)
    document = Document.objects.get(id=document_id,chama=chama)
    file_path = document.file.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{document.name}"'
        return response
    else:
        return JsonResponse({'error': 'File not found'}, status=404) 


@login_required(login_url='/user/Login')
def chamas(request):
    return render(request,'chamas/chamas-home.html',{})


@login_required(login_url='/user/Login')
def your_chamas(request):
    user = request.user

    chama_memberships = ChamaMember.objects.filter(user=user, active=True)
    chama_list = []
    for chama_membership in chama_memberships:
        chama = chama_membership.group
        chama_name = chama.name
        member_count = chama.member.count() 
        id = chama.id
       
        is_admin = chama_membership.role.name == 'admin'  
        chama_list.append({
            'name': chama_name,
            'member_count': member_count,
            'is_admin': is_admin,
            'id':id
        })

    # logger.info("Chamas page rendered succesfully")
    return render(request, 'chamas/your-chamas.html', {'chama_list': chama_list})


def create_chama_type(request):
    if request.method == 'POST':
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
    else:
        data = {
            'status':'failed',
            'message':'wrong http method'
        }
        return JsonResponse(data,status=405)

def new_chama_form(request):
    roles = Role.objects.all()
    types = ChamaType.objects.all()
    return render(request,'chamas/new-chama.html',{'roles':roles,'types':types})


@login_required(login_url='/user/Login')
def create_chama(request):
    if request.method == 'POST':
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
       
    else:
        data = {
            'status':'failed',
            'message':'Invalid http method'
        }
        return JsonResponse(data,status=200)


@login_required(login_url='/user/Login')
def add_member_to_chama(request):
    if request.method == 'POST':

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
    else:
        data = {
            'status':'failed',
            'message':'Invalid http method'
        }
        print(data)
        return JsonResponse(data,status=405)

def audit_chama_members(chama_id):
    chama = Chama.objects.get(pk=chama_id)
    for member in chama.member.all():
        user = User.objects.filter(username=member.member_id).first()
        if user:
            member.user = user
            member.save()


@login_required(login_url='/user/Login')    
def remove_member_from_chama(request, member_id, chama_id):
    chama = get_object_or_404(Chama, pk=chama_id)

    if chama:
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
    else:
        data = {
            'status':'failed',
            'message':'Invalid user or chama id.'
        }
        return JsonResponse(data,status=400)

@login_required(login_url='/user/Login')
def members(request,chama_id):

    chama = Chama.objects.get(pk=chama_id)
    members = ChamaMember.objects.filter(active=True,group=chama).all()
    audit_chama_members(chama.id)

    if chama:
        print(chama.name.__str__(),chama.member.count())
        return render(request,'chamas/members.html',{
            'group':chama,
            'members':members,
            'roles':Role.objects.all()
        })


@login_required(login_url='/user/Login')
def member_details(request, chama_member_id, group):
    try:
        chama = get_object_or_404(Chama, pk=group)
        member = get_object_or_404(ChamaMember, group=chama, id=chama_member_id)
        
        # Retrieve last 4 contributions
        contributions = ContributionRecord.objects.filter(member=member).order_by('-date_created')[:4]
        contribution_dicts = [model_to_dict(contribution) for contribution in contributions]
        for contribution in contribution_dicts:
            type = Contribution.objects.get(pk=contribution['contribution'])
            contribution['contribution'] = type.name

        # Retrieve last 4 loans
        loans = LoanItem.objects.filter(member=member).order_by('-start_date')[:4]
        loan_dicts = [model_to_dict(loan) for loan in loans]
        for loan in loan_dicts:
            if loan['start_date']:
                loan['start_date'] = loan['start_date'].strftime('%d/%m/%Y %H:%M:%S')
            if loan['end_date']:
                loan['end_date'] = loan['end_date'].strftime('%d/%m/%Y %H:%M:%S')


        # Retrieve last 4 fines
        fines = FineItem.objects.filter(member=member).order_by('-created')[:4]
        fine_dicts = [model_to_dict(fine) for fine in fines]
        for fine in fine_dicts:
            type = FineType.objects.get(pk=fine['fine_type'])
            fine['fine_type'] = type.name
            fine['last_updated'] = loan['last_updated'].strftime('%d/%m/%Y %H:%M:%S')

        # Serialize member and related objects to dictionary
        member_dict = model_to_dict(member)
        member_dict['role'] = member.role.name
        if member.profile:  # Check if profile exists before accessing its URL
            member_dict['profile'] = member.profile.url
        else:
            member_dict['profile'] = None

        data = {
            'status': 'success',
            'member': member_dict,
            'contributions': contribution_dicts,
            'loans': loan_dicts,
            'fines': fine_dicts
        }
        return JsonResponse(data, status=200)
    
    except (Chama.DoesNotExist, ChamaMember.DoesNotExist):
        data = {
            'status': 'failed',
            'message': 'Chama or member could not be found.'
        }
        return JsonResponse(data, status=404)

def ascertain_member_role(request,chama_id):
    user = request.user
    chama = Chama.objects.get(pk=chama_id)
    member = None
    for member in chama.member.all():
        if member.user == user:
            member = member
            break
    
    data = {
        'status':'success',
        'role':member.role.name
    }
    return JsonResponse(data,status=200)



#Contribution Handlers
@login_required(login_url='/user/Login')
@is_user_chama_member
def create_contribution(request,chama_id):
    if request.method == 'POST':
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
        
@login_required(login_url='/user/Login')
@is_user_chama_member
def contributions(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)
    contributions = Contribution.objects.filter(chama=chama.id).all()
    members = ChamaMember.objects.filter(group=chama).all()
    fines = FineType.objects.filter(chama=chama).all()
    return render(request,'chamas/contributions.html',{'contributions':contributions,'members':members,'fine_types':fines})


@login_required(login_url='/user/Login')
@is_user_chama_member
def contributions_details(request, chama_id):
    if request.method == 'POST':
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
                'records': serialize_paginated_records(records_page),
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

    else:
        data = {
            'status': 'error',
            'message': 'Invalid HTTP method. Only POST is allowed.',
        }
        return JsonResponse(data, status=405)


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

@login_required(login_url='/user/Login')
@is_user_chama_member
def create_contribution_record(request, chama_id):
    if request.method == 'POST':
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
    else:
        data = {
            'status': 'failed',
            'message': 'Invalid HTTP method'
        }

        return JsonResponse(data, status=405)
    

@login_required(login_url='/user/Login')
def pay_contribution(request, contribution_id):
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
  
#----------LOAN HANDLERS------------------
@login_required(login_url='/user/Login')
@is_user_chama_member
def chama_loans(request, chama_id):
    chama = Chama.objects.get(pk=chama_id)

    # Get all loan types associated with the chama
    loan_types = LoanType.objects.filter(chama=chama).all()

    # Get all loans associated with the chama and loan types
    chama_loans = []
    for loan_type in loan_types:
        for loan in loan_type.loan_records.all():
            chama_loans.append(loan)
            
    # Get All members of the chama
    members = ChamaMember.objects.filter(active=True,group=chama).all()
    member = None
    for member in members:
        if member.user == request.user:
            member = member
            break
    my_loans = LoanItem.objects.filter(chama=chama,member=member,status='active').all()

    # Get all loan applications for the chama
    applications = LoanItem.objects.filter(member__group=chama, status='application').all()

    active_loans = LoanItem.objects.filter(member__group = chama,status='active').all()
     

    context = {
        'loans': chama_loans,
        'loan_types': loan_types,
        'applications': applications,
        'active_loans':active_loans,
        'members': members,
        'my_loans':my_loans
        
    }

    return render(request, 'chamas/loans.html', context)
            

@login_required(login_url='/user/Login')
@is_user_chama_member  
def create_loan_type(request,chama_id):
    if request.method == 'POST':
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
        
        
@login_required(login_url='/user/Login')
@is_user_chama_member
def issue_loan(request, chama_id):
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


@login_required(login_url='/user/Login')
def apply_loan(request,chama_id):
    if request.method == 'POST':
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


@login_required(login_url='/user/Login')
@is_user_chama_member
def accept_loan_request(request, chama_id, loan_id):
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


@login_required(login_url='/user/Login')
@is_user_chama_member
def decline_loan(request,loan_id,chama_id):
    loan = LoanItem.objects.get(pk=loan_id)
    loan.status = 'declined'
    loan.last_updated = timezone.now()

    loan.save()

    data = {
        'status':'success',
        'message':'loan declined succesfully'

    }
    return JsonResponse(data,status = 200)


@login_required(login_url='/user/Login')
def update_loan(request, loan_id):
    loan = LoanItem.objects.get(pk=loan_id)

    if request.method == 'POST':
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


#------------Fine handlers---------------------------------------------
@login_required(login_url='/user/Login')
@is_user_chama_member
def chama_fines(request,chama_id):

    chama = Chama.objects.get(pk=chama_id)

    loan_types = LoanType.objects.filter(chama=chama).all()
    loans = []
    for loan_type in loan_types:
        for loan in loan_type.loan_records.all():
            if loan.status == 'active':
                loans.append(loan)
            
    members = ChamaMember.objects.filter(group=chama).all()
    fine_types = FineType.objects.filter(chama=chama).all()

    active_fines = []
    contribution_fines = []
    for type in fine_types:
        type_fines = FineItem.objects.filter(fine_type=type,status = 'active').all()
        for fine in type_fines:
            if fine.forLoan:
                active_fines.append(fine)
            if fine.forContribution:
                contribution_fines.append(fine)

    my_contribution_fines = []
    my_loan_fines = []
    member = None

    for member in chama.member.all():
        if member.user == request.user:
            member = member
            break

    for type in fine_types:
        my_fines = FineItem.objects.filter(fine_type=type,member=member,status='active').all()
        for fine in my_fines:
            if fine.forContribution:
                my_contribution_fines.append(fine)
            elif fine.forLoan:
                my_loan_fines.append(fine)

    contributions = Contribution.objects.filter(chama=chama).all()

    
    context = {
        'loan_types':loan_types,
        'members':members,
        'fine_types':fine_types,
        'fines':active_fines,
        'loans':loans,
        'contributions':contributions,
        'contribution_fines':contribution_fines,
        'my_loan_fines':my_loan_fines,
        'my_contribution_fines':my_contribution_fines
    }

    return render(request,'chamas/fines.html',context)

@login_required(login_url='/user/Login')
@is_user_chama_member
def create_fine_type(request,chama_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        amount = int(data.get('amount'))
        description = str(data.get('description'))
        chama = Chama.objects.get(pk = chama_id)

        try:
            new_fine_type = FineType.objects.create(
                name = name,
                amount=amount,
                description=description,
                chama=chama
            )

            data = {
                'status':'success',
                'message':'fine type created succesfully',
                'fine_type':model_to_dict(new_fine_type)
            }
            return JsonResponse(data,status=200)

        except Exception as e:

            data = {
                'status':'failed',
                'message':f'an error occcurred:{e}'
            }

            return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'invalid http method'
        }
        return JsonResponse(data,status=200)
    

@login_required(login_url='/user/Login')
def fine_contribution(request,contribution_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        contribution_item = ContributionRecord.objects.get(pk=contribution_id)
        contribution = contribution_item.contribution
        member = contribution_item.member
        fine = FineType.objects.get(pk=data.get('fine'))
        contribution_balance = contribution_item.balance

        try:
            new_fine_object = FineItem.objects.create(
                fine_type = fine,
                member = member,
                fine_amount = fine.amount,
                paid_fine_amount = 0.00,
                fine_balance = fine.amount,
                contribution = contribution,
                forLoan = False,
                forContribution = True,
                contribution_balance = Decimal(contribution_balance)
            )
            new_cashflow_object = CashflowReport.objects.create(
                        object_date = new_fine_object.created,
                        member = new_fine_object.member,
                        type = 'imposed fine',
                        amount = new_fine_object.fine_amount,
                        chama = new_fine_object.fine_type.chama,
                        forGroup = False
                    )
            fine = model_to_dict(new_fine_object)
            fine['member'] = member.name
            fine['fine_type'] = new_fine_object.fine_type.name

            data = {
                'status':'success',
                'message':f'Fine imposed on {member.name} successfully',

            }

            return JsonResponse(data,status=200)
    
        except Exception as e:
            data = {
                'status':'failed',
                'message':'an error occured,the fine could not be imposed'
            }

            return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'Invalid http methods'
        }

        return JsonResponse(data,status=200)


@login_required(login_url='/user/Login')
def impose_fine(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        loan = LoanItem.objects.get(pk=int(data.get('loan_id')))

        member = loan.member
        fine_type = FineType.objects.get(pk = int(data.get('fine_type')))


        loan_amount = loan.amount
        loan_balance = loan.balance
        fine_amount = fine_type.amount
        paid_fine_amount = 0.00
        fine_balance = fine_type.amount

        try:
            new_fine_object = FineItem.objects.create(
                member = member,
                fine_type = fine_type,
                loan_amount=loan_amount,
                loan_balance=loan_balance,
                fine_amount=fine_amount,
                paid_fine_amount = paid_fine_amount,
                fine_balance=fine_balance,
                loan = loan,
                forLoan = True
            )

            new_cashflow_object = CashflowReport.objects.create(
                        object_date = new_fine_object.created,
                        member = new_fine_object.member,
                        type = 'imposed fine',
                        amount = new_fine_object.fine_amount,
                        chama = new_fine_object.fine_type.chama,
                        forGroup = False
                    )

            data = {
                'status' :'success',
                'message':f'Fine imposed on {member.name} succesfully.'
            }

            return JsonResponse(data,status=200)


        except Exception as e:
            data = {
                'status':'failed',
                'message':f'An error occurred:{e}'
            }
            return JsonResponse(data,status=200)
        

@login_required(login_url='/user/Login')
def update_fine(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fine = FineItem.objects.get(pk = int(data.get('fine_id')))
        loan = fine.loan

        if fine.forLoan:
            fine.loan_balance = loan.balance
            fine.paid_fine_amount += int(data.get('fine-amount'))
            fine.fine_balance -= int(data.get('fine-amount'))
            fine.last_updated = timezone.now()
            if fine.fine_balance <= 0.00:
                fine.status = 'cleared'
            
            fine.save()
        
        elif fine.forContribution:
            fine.paid_fine_amount += int(data.get('fine-amount'))
            fine.fine_balance -= int(data.get('fine-amount'))
            fine.last_updated = timezone.now()
            if fine.fine_balance <= 0.00:
                fine.status = 'cleared'

            fine.save()

        new_cashflow_object = CashflowReport.objects.create(
            object_date = fine.created,
            type = 'fine payment',
            amount = Decimal(data.get('fine-amount')),
            chama = fine.fine_type.chama,
            forGroup = False,
            member = fine.member
        )

        

        data = {
            'status':'success',
            'message':'fine updated succesfully',
            'fine':model_to_dict(fine)
        }

        return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'invalid http method'
        }

        return JsonResponse(data,status=200)


#--------------Expense handlers------------------------------------
@login_required(login_url='/user/Login')
@is_user_chama_member
def expenses(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)

    expenses = Expense.objects.filter(chama=chama).all()
  

    return render(request,'chamas/expenses.html',{
        'expenses':expenses
    })


@login_required(login_url='/user/Login')
@is_user_chama_member
def create_expense(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)

    if request.method == 'POST':
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
        

#finance handlers
@login_required(login_url='/user/Login')
@is_user_chama_member
def finances(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)
    # profile = get_object_or_404(Profile, owner=request.user)
    # chama_member = get_object_or_404(ChamaMember, mobile=profile.phone, group=chama)

    chama = Chama.objects.get(pk=chama_id)
    chama_member = None
    for member in chama.member.all():
        if member.user == request.user:
            chama_member = member
            break

    my_savings = Paginator(Saving.objects.filter(forGroup=False,chama=chama, owner=chama_member).order_by('-id').all(),6)
    my_savings = my_savings.page(1)

    individual_savings = Paginator(Saving.objects.filter(forGroup=False,chama=chama).order_by('-id').all(),6)
    individual_savings = individual_savings.page(1)

    group_savings = Paginator(Saving.objects.filter(forGroup=True,chama=chama).order_by('-id').all(),6)
    group_savings = group_savings.page(1)

    group_saving_tot = 0.00
    for saving in group_savings:
        group_saving_tot += int(saving.amount)

    group_investments = Paginator(Investment.objects.filter(chama=chama).order_by('-id').all(),6)
    group_investments = group_investments.page(1)

    group_investments_tot = 0.00
    for investment in group_investments:
        group_investments_tot += int(investment.amount)

    group_investment_incomes = Paginator(Income.objects.filter(chama=chama,forGroup=True).order_by('-id').all(),6)
    group_investment_incomes = group_investment_incomes.page(1)

    group_investment_incomes_tot = 0.00
    for income in group_investment_incomes:
        group_investment_incomes_tot += int(income.amount)

    individual_investment_income = Paginator(Income.objects.filter(chama=chama,forGroup=False).order_by('-id').all(),6)
    individual_investment_income = individual_investment_income.page(1)
    
    my_investment_income = Paginator(Income.objects.filter(chama=chama,forGroup=False, owner=chama_member).order_by('-id').all(),6)
    my_investment_income = my_investment_income.page(1)

    members = ChamaMember.objects.filter(group=chama,active=True).all()
    saving_types = SavingType.objects.all()

    investments = Investment.objects.filter(chama=chama).all()




    context = {
         'saving_types':saving_types,
        'members':members,
        'individual_savings':individual_savings,
        'my_savings':my_savings,
        'group_savings':group_savings,
        'group_savings_tot':group_saving_tot,
        'group_investments':group_investments,
        'group_investments_tot':group_investments_tot,
        'group_investment_incomes':group_investment_incomes,
        'group_investment_incomes_tot':group_investment_incomes_tot,
        'individual_investment_income':individual_investment_income,
        'my_investment_income':my_investment_income,
        'investments':investments

    }

    return render(request,'chamas/finances.html',context)


@login_required(login_url='/user/Login')
@is_user_chama_member
def create_saving(request,chama_id):
    if request.method == 'POST':
        try:
            chama = Chama.objects.get(pk=chama_id)
            data = json.loads(request.body)
            owner = data.get('owner')
            amount = data.get('amount')
            saving_type = data.get('saving-type')
            saving_type = SavingType.objects.get(pk=int(saving_type))


            if owner == 'group':
                forGroup = True
                new_saving = Saving.objects.create(
                    chama = chama,
                    forGroup = forGroup,
                    amount=amount,
                    saving_type = saving_type

                )

            else:
                forGroup = False
                owner = ChamaMember.objects.get(pk=int(owner))
                new_saving = Saving.objects.create(
                    owner = owner,
                    chama = chama,
                    forGroup = forGroup,
                    amount = amount,
                    saving_type = saving_type
                )
            
            data = {
                'status':'success',
                'message':'Saving created succesfully',
                'saving':model_to_dict(new_saving)
            }
            return JsonResponse(data,status=200)

        except Exception as e:
            data = {
                'status':'failed',
                'message':f'an error occured:{e}'
            }
            return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'Invalid http method'
        }
        return JsonResponse(data,status=200)
        
@login_required(login_url='/user/Login')
@is_user_chama_member
def create_investment(request,chama_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        amount = data.get('amount')
        date = data.get('date')

        chama = Chama.objects.get(pk=chama_id)

        try:
            new_investment = Investment.objects.create(
                name = name,
                amount = amount,
                chama = chama,
                user_date = date
            )
            data = {
                'status':'success',
                'message':'New investment created succesfully',
                'investment':model_to_dict(new_investment)
            }

            return JsonResponse(data,status=200)

        except Exception as e:
            data = {
                'status':'failed',
                'message':f'an error occurred: {e}'
            }

            return JsonResponse(data,status=200)

        
@login_required(login_url='/user/Login')
@is_user_chama_member
def create_income(request,chama_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        owner = data.get('owner')
        chama = Chama.objects.get(pk=chama_id)
        amount = data.get('amount')
        date = data.get('date')
        investment = data.get('investment-scheme')

        if investment == 'others':
            try:
                investment = Investment.object.get(name='others',chama=chama)

            except Exception as e:
                new_investment = Investment.objects.create(name='others',amount=Decimal('0.00'),chama=chama)
                investment = new_investment
        else:
            investment = Investment.objects.get(pk=int(investment))
        
        if owner == 'group':
            forGroup = True
            new_income = Income.objects.create(
                name = name,
                chama = chama,
                forGroup = forGroup,
                amount = amount,
                user_date = date,
                investment = investment
            )

        else:
            forGroup = False
            owner = ChamaMember.objects.get(pk=int(owner))
            new_income = Income.objects.create(
                name = name,
                owner = owner,
                chama = chama,
                forGroup = forGroup,
                amount = amount,
                investment = investment
            )

        data = {
            'status':'success',
            'message':'new income created succesfully',
            'income':model_to_dict(new_income)
        }

        return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'invalid http method'
        }

        return JsonResponse(data,status=200)

        

#reports handlers
@login_required(login_url='/user/Login')
@is_user_chama_member
def reports(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)
    

    group_investment_incomes = Paginator(Income.objects.filter(chama=chama,forGroup=True).order_by('-id').all(),6).page(1)
    _group_investment_incomes = list(group_investment_incomes.object_list.values())
    for income in _group_investment_incomes:
        income['user_date'] = income['user_date'].strftime("%Y-%m-%d")
        income['date'] = income['date'].strftime("%Y-%m-%d")
        income['amount'] = float(income['amount'])

        try:
            i = Investment.objects.get(pk=int(income['investment_id']))
            income['investment_id'] = i.name
        except:
            pass
    group_investment_incomes = json.dumps(_group_investment_incomes)

    individual_investment_incomes = Paginator(Income.objects.filter(chama=chama,forGroup=False).order_by('-id'),10).page(1)
    _individual_investment_incomes = list(individual_investment_incomes.object_list.values())
    for income in _individual_investment_incomes:
        income['user_date'] = income['user_date'].strftime("%Y-%m-%d")
        income['date'] = income['date'].strftime("%Y-%m-%d")
        income['amount'] = float(income['amount'])

    
        try:
            i = Investment.objects.get(pk=int(income['investment_id']))
            income['investment_id'] = i.name
        except Exception as e:
            pass

        try:
            m = ChamaMember.objects.get(pk=int(income['owner_id']))
            income['owner_id'] = m.name
        except Exception as e:
            
            income['owner_id'] = 'group'
    individual_investment_incomes = json.dumps(_individual_investment_incomes)

    individual_savings = Paginator(Saving.objects.filter(forGroup=False,chama=chama).order_by('-id').all(),10).page(1)
    _individual_savings = list(individual_savings.object_list.values())
    for saving in _individual_savings:
        saving['date'] = saving['date'].strftime("%Y-%m-%d")
        saving['amount'] = float(saving['amount'])
       
         
        try:
            m = ChamaMember.objects.get(pk=int(saving['owner_id']))
            saving['owner_id'] = m.name
        except:
            pass

        try:
            t = SavingType.objects.get(pk=saving['saving_type_id'])
            saving['saving_type_id'] = t.name

        except:
            pass

    individual_savings = json.dumps(_individual_savings)


    group_savings = Paginator(Saving.objects.filter(forGroup=True,chama=chama).order_by('-id').all(),6).page(1)
    _group_savings = list(group_savings.object_list.values())
    for saving in _group_savings:
        saving['date'] = saving['date'].strftime("%Y-%m-%d")
        saving['amount'] = float(saving['amount'])

        try:
            t = SavingType.objects.get(pk=saving['saving_type_id'])
            saving['saving_type_id'] = t.name

        except:
            pass
    group_savings = json.dumps(_group_savings)
    c = ContributionRecord.objects.order_by('-id').all()

    group_contributions = Paginator(ContributionRecord.objects.filter(chama=chama).order_by('-date_created').all(),10).page(1)
    _group_contributions = list(group_contributions.object_list.values())
    for contribution in _group_contributions:
        contribution['date_created'] = contribution['date_created'].strftime("%Y-%m-%d")
        contribution['last_updated'] = contribution['last_updated'].strftime("%Y-%m-%d")
        contribution['amount_paid'] = float(contribution['amount_paid'])
        contribution['balance'] = float(contribution['balance'])
        contribution['amount_expected'] = float(contribution['amount_expected'])

        try:
            c = Contribution.objects.get(pk=int(contribution['contribution']))
            contribution['contribution'] = c.id
            contribution['scheme_name'] = c.name

        except:
            pass

        try:
            m = ChamaMember.objects.get(pk=int(contribution['member_id']))
            contribution['member_id'] = m.id
            contribution['member_name'] = m.name

        except:
            pass
    group_contributions = json.dumps(_group_contributions)
    
    chama_expenses = Paginator(Expense.objects.filter(chama=chama).order_by('-created_on'),10).page(1)
    _chama_expenses = list(chama_expenses.object_list.values())
    expenses_tot = 0
    for expense in _chama_expenses:
        expense['created_on'] = expense['created_on'].strftime("%Y-%m-%d")
        expense['amount'] = float(expense['amount'])

        try:
            m = ChamaMember.objects.get(pk=int(expense['created_by_id']))
            expense['created_by_id'] = m.name
        except:
            pass
        expenses_tot += expense['amount']
    chama_expenses = json.dumps(_chama_expenses)
    
    

    
    compute_group_savings = Paginator(Saving.objects.filter(forGroup=True,chama=chama).order_by('-id').all(),10).page(1)
    group_saving_tot = 0.00
    for saving in compute_group_savings:
        group_saving_tot += int(saving.amount)


    compute_group_investment_incomes = Paginator(Income.objects.filter(chama=chama,forGroup=True).order_by('-id').all(),10).page(1)
    group_investment_incomes_tot = 0.00
    for income in compute_group_investment_incomes:
        group_investment_incomes_tot += int(income.amount)

    
    loans = Paginator(LoanItem.objects.filter(chama=chama).order_by('-applied_on').all(),10).page(1)
    _loans = list(loans.object_list.values())
    for loan in _loans:
        if loan['start_date'] is not None:
            loan['start_date'] = loan['start_date'].strftime("%Y-%m-%d")
        if loan['end_date'] is not None:
            loan['end_date'] = loan['end_date'].strftime("%Y-%m-%d")
        if loan['amount'] is not None: 
            loan['amount'] = float(loan['amount'])
        if loan['total_paid'] is not None:
            loan['total_paid'] = float(loan['total_paid'])
        if loan['balance'] is not None:
            loan['balance'] = float(loan['balance'])
        if loan['intrest_rate'] is not None:
            loan['intrest_rate'] = float(loan['intrest_rate'])

        try:
            m = ChamaMember.objects.get(pk=int(loan['member_id']))
            loan['member_id'] = m.name
        except:
            pass

        try:
            t = LoanType.objects.get(pk=int(loan['type_id']))
            loan['type_id'] = t.name
        except:
            pass
    active_loans = json.dumps(_loans, cls=DjangoJSONEncoder)
    
    fine_types = FineType.objects.filter(chama=chama).all()
    _fines = []

    for fine_type in fine_types:
        _fines.extend(fine_type.fine_items.all())

    
    fines = json.dumps([{
    'member': fine.member.name if fine.member else None,
    'type': fine.fine_type.name,
    'loan_amount': float(fine.loan_amount) if fine.loan_amount else None,
    'loan_balance': float(fine.loan_balance) if fine.loan_balance else None,
    'fine_amount': float(fine.fine_amount),
    'paid_fine_amount': float(fine.paid_fine_amount),
    'fine_balance': float(fine.fine_balance),
    'status': fine.status,
    'created': fine.created.strftime('%Y-%m-%d'),
    'last_updated': fine.last_updated.strftime('%Y-%m-%d'),
    'forLoan': fine.forLoan,
    'forContribution': fine.forContribution,
    'contribution_balance': float(fine.contribution_balance) if fine.contribution_balance else None
    }   for fine in _fines if fine.status == 'cleared'], cls=DjangoJSONEncoder)


    unpaid_fines = json.dumps([{
    'member': fine.member.name if fine.member else None,
    'type': fine.fine_type.name,
    'loan_amount': float(fine.loan_amount) if fine.loan_amount else None,
    'loan_balance': float(fine.loan_balance) if fine.loan_balance else None,
    'fine_amount': float(fine.fine_amount),
    'paid_fine_amount': float(fine.paid_fine_amount),
    'fine_balance': float(fine.fine_balance),
    'status': fine.status,
    'created': fine.created.strftime('%Y-%m-%d'),
    'last_updated': fine.last_updated.strftime('%Y-%m-%d'),
    'forLoan': fine.forLoan,
    'forContribution': fine.forContribution,
    'contribution_balance': float(fine.contribution_balance) if fine.contribution_balance else None
    } for fine in _fines if fine.status == 'active'], cls=DjangoJSONEncoder)


    chama_cashflow_report = Paginator(CashflowReport.objects.filter(chama=chama).order_by('-date_created').all(),10).page(1)
    _chama_cashflow_reports = list(chama_cashflow_report.object_list.values())
    for report in _chama_cashflow_reports:
        report['object_date'] = report['object_date'].strftime("%Y-%m-%d")
        report['date_created'] = report['date_created'].strftime("%Y-%m-%d")
        report['amount'] = float(report['amount'])

        
        try:
            m = ChamaMember.objects.get(pk=int(report['member_id']))
            report['member_id'] = m.name
        except:
            pass 
    chama_cashflow_reports = json.dumps(_chama_cashflow_reports)

   

    total_contributions = Decimal('0.00')
    total_loan_disbursment = Decimal('0.00')
    total_loan_repayments = Decimal('0.00')
    total_issued_fines = Decimal('0.00')
    total_fines_collected = Decimal('0.00')
    total_expenses = Decimal('0.00')
    unpaid_fines_total = total_issued_fines - total_fines_collected

    compute_chama_cashflow_reports = Paginator(CashflowReport.objects.filter(chama=chama).order_by('-date_created').all(),5).page(1)
    for report in compute_chama_cashflow_reports:
        if report.type == 'contribution':
            total_contributions += Decimal(report.amount)
            

        elif report.type == 'loan disbursment':
            total_loan_disbursment += Decimal(report.amount)

        elif report.type == 'loan payment':
            total_loan_repayments += Decimal(report.amount)

        elif report.type == 'imposed fine':
            total_issued_fines += Decimal(report.amount)

        elif report.type == 'fine payment':
            total_fines_collected += Decimal(report.amount)

        elif report.type == 'expense':
            total_expenses += Decimal(report.amount)

    net_cashflow = (
    total_contributions 
    + total_loan_disbursment 
    + total_loan_repayments 
    + total_issued_fines 
    + total_fines_collected 
    + total_expenses
    )
    print('total contributions:',total_contributions)

    member = None
    for member in chama.member.all():
        if member.user:
            if member.user == request.user:
                member = member
                break

    my_reports = Paginator(CashflowReport.objects.filter(chama=chama,member=member).order_by('-date_created').all(),10).page(1)
    _my_reports = list(my_reports.object_list.values())
    for report in _my_reports:
        report['object_date'] = report['object_date'].strftime('%Y-%m-%d')
        report['date_created'] = report['date_created'].strftime('%Y-%m-%d')
        report['amount'] = float(report['amount'])

        try:
            m = ChamaMember.objects.get(pk=report['member_id'])
            report['member_id'] = m.name

        except:
            pass
    my_reports = json.dumps(_my_reports)


    my_investment_incomes = Paginator(Income.objects.filter(chama=chama,owner=member).order_by('-date').all(),10).page(1)
    _my_investment_income = list(my_investment_incomes.object_list.values())
    for income in _my_investment_income:
        income['date'] = income['date'].strftime('%Y-%m-%d')
        income['user_date'] = income['user_date'].strftime('%Y-%m-%d')
        income['amount'] = float(income['amount'])

        try:
            o = ChamaMember.objects.get(pk=int(income['owner_id']))
            income['owner_id'] = o.name

        except:
            pass

        try:
            i = Investment.objects.get(pk=int(income['investmnet_id']))
            income['investment'] = i.name
        except:
            pass
    my_investment_incomes = json.dumps(_my_investment_income)
    

    my_total_contributions = Decimal('0.00')
    my_total_loan_disbursment = Decimal('0.00')
    my_total_loan_repayments = Decimal('0.00')
    my_total_issued_fines = Decimal('0.00')
    my_total_fines_collected = Decimal('0.00')
    my_total_expenses = Decimal('0.00')

    compute_my_reports = Paginator(CashflowReport.objects.filter(chama=chama,member=member).order_by('-date_created').all(),10).page(1)
    for report in compute_my_reports:
        if report.type == 'contribution':
            my_total_contributions += Decimal(report.amount)

        elif report.type == 'loan disbursment':
            my_total_loan_disbursment += Decimal(report.amount)

        elif report.type == 'loan payment':
            my_total_loan_repayments += Decimal(report.amount)

        elif report.type == 'imposed fine':
            my_total_issued_fines += Decimal(report.amount)

        elif report.type == 'fine payment':
            my_total_fines_collected += Decimal(report.amount)

        elif report.type == 'expense':
            my_total_expenses += Decimal(report.amount)

    my_net_cashflow = (
    my_total_contributions 
    + my_total_loan_disbursment 
    + my_total_loan_repayments 
    + my_total_issued_fines 
    + my_total_fines_collected 
    + my_total_expenses
    )

    my_contributions = Paginator(ContributionRecord.objects.filter(chama=chama,member=member).order_by('-id'),10).page(1)
    tot = 0.00
    for contribution in my_contributions:
        tot += float(contribution.amount_paid)
        print(contribution.amount_paid)

    contribution_schemes = Contribution.objects.filter(chama=chama).all()

    

    

    context = {
        'loans':loans,
        'unpaid_loans':active_loans,
        'group_investment_incomes':group_investment_incomes,
        'group_investment_incomes_tot':group_investment_incomes_tot,
        'member_investment_income':individual_investment_incomes,
        'individual_saving_report':individual_savings,
        'chama_cashflow_reports':chama_cashflow_reports,
        'net_cashflow':net_cashflow,
        'group_saving_report':group_savings,
        'group_savings_tot':group_saving_tot,
        'collected_fines':fines,
        'unpaid_fines':unpaid_fines,
        'members':ChamaMember.objects.filter(group=chama,active=True).all(),
        'total_contributions':total_contributions,
        'total_loan_disbursment':total_loan_disbursment,
        'total_loan_repayments':total_loan_repayments,
        'total_issued_fines':total_issued_fines,
        'total_fines_collected':total_fines_collected,
        'total_expenses':total_expenses,
        'my_reports':my_reports,
        'my_total_loan_disbursment':my_total_loan_disbursment,
        'my_total_loan_repayments':my_total_loan_repayments,
        'my_total_issued_fines':my_total_issued_fines,
        'my_total_fines_collected':my_total_fines_collected,
        'my_total_expenses':my_total_expenses,
        'my_net_cashflow':my_net_cashflow,
        'group_contributions':group_contributions,
        'unpaid_fines_total':unpaid_fines_total,
        'my_investment_incomes':my_investment_incomes,
        'my_contributions':my_contributions,
        'my_tot_contributions':tot,
        'chama_expense_reports':chama_expenses,
        'expenses_tot':expenses_tot,
        'schemes':contribution_schemes
        
    }



    return render(request,'chamas/reports.html',context)

#------------------------Report download handlers-----------------
def download_loan_report(request, chama_id):
    # ─────────────────────────────────────────────
    # 1) Fetch your Chama and its LoanItems
    # ─────────────────────────────────────────────
    chama = Chama.objects.get(pk=chama_id)
    loans = LoanItem.objects.filter(chama=chama)

    # ─────────────────────────────────────────────
    # 2) Prepare PDF response & document
    # ─────────────────────────────────────────────
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_loan_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # ─────────────────────────────────────────────
    # 3) Header callback for every page
    # ─────────────────────────────────────────────
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-60,
            "Loan Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-75,
            datetime.now().strftime("%Y-%m-%d")
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # ─────────────────────────────────────────────
    # 4) Build your table data & style
    # ─────────────────────────────────────────────
    data = [[
        'Member Name', 'Loan Type',
        'Start Date', 'Due Date',
        'Amount', 'Total Paid',
        'Balance', 'Status'
    ]]
    for loan in loans:
        data.append([
            loan.member.name,
            loan.type.name,
            loan.start_date.strftime('%Y-%m-%d'),
            loan.end_date.strftime('%Y-%m-%d'),
            f'ksh {loan.amount}',
            f'ksh {loan.total_paid}',
            f'ksh {loan.balance}',
            loan.status,
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # ─────────────────────────────────────────────
    # 5) Assemble & build
    # ─────────────────────────────────────────────
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response



@login_required(login_url='/user/Login')
@is_user_chama_member
def download_loan_repayment_schedule(request, chama_id):
    # 1) Fetch Chama and active Loans
    chama = Chama.objects.get(pk=chama_id)
    loans = LoanItem.objects.filter(chama=chama, status='active')

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_loan_repayment_schedule.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-60,
            "Loan Repayment Schedule"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-75,
            datetime.now().strftime("%Y-%m-%d")
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data & style
    data = [[
        'Member Name', 'Loan Type', 'Start Date',
        'Due Date', 'Amount', 'Total Paid',
        'Balance', 'Status', 'Repayment Term'
    ]]
    for loan in loans:
        data.append([
            loan.member.name,
            loan.type.name,
            loan.start_date.strftime('%Y-%m-%d'),
            loan.end_date.strftime('%Y-%m-%d'),
            f'ksh {loan.amount}',
            f'ksh {loan.total_paid}',
            f'ksh {loan.balance}',
            loan.status,
            loan.due,
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 5) Assemble & build
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response

    
@login_required(login_url='/user/Login')
@is_user_chama_member
def download_group_investment_income(request, chama_id):
    # 1) Fetch Chama and group Income data
    chama   = Chama.objects.get(pk=chama_id)
    incomes = Income.objects.filter(chama=chama, forGroup=True)

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_group_investment_income.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-60,
            "Group Investment Income"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-75,
            datetime.now().strftime("%Y-%m-%d")
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data & style
    data = [[
        'Income Name', 'Investment',
        'Date', 'Amount'
    ]]
    for inc in incomes:
        data.append([
            inc.name,
            inc.investment.name,
            inc.date.strftime('%Y-%m-%d'),
            f'ksh {inc.amount}',
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 5) Assemble & build
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response

    
@login_required(login_url='/user/Login')
@is_user_chama_member
def download_member_investment_income(request, chama_id):
    # 1) Fetch Chama and Income data
    chama = Chama.objects.get(pk=chama_id)
    member_id = request.GET.get('member-id', None)

    if member_id:
        member = ChamaMember.objects.get(pk=int(member_id))
        incomes = Income.objects.filter(chama=chama, forGroup=False, owner=member)
    else:
        incomes = Income.objects.filter(chama=chama, forGroup=False)

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_member_investment_income.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "Member Investment Income"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime("%Y-%m-%d")
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data & style
    data = [[
        'Income Name', 'Member Name',
        'Investment', 'Amount', 'Date'
    ]]
    for income in incomes:
        data.append([
            income.name,
            income.owner.name,
            income.investment.name,
            f'ksh {income.amount}',
            income.date.strftime('%Y-%m-%d')
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 5) Assemble & build
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response




@login_required(login_url='/user/Login')
@is_user_chama_member
def download_individual_saving_report(request, chama_id):
    # 1) Fetch Chama and individual saving data
    chama = Chama.objects.get(pk=chama_id)
    member_id = request.GET.get('member-id', None)

    if member_id:
        member  = ChamaMember.objects.get(pk=int(member_id))
        savings = Saving.objects.filter(chama=chama, forGroup=False, owner=member)
    else:
        savings = Saving.objects.filter(chama=chama, forGroup=False)

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_individual_savings_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='main'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-60,
            "Individual Savings Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data & style
    data = [[
        'Member', 'Amount', 'Type', 'Date'
    ]]
    for s in savings:
        data.append([
            s.owner.name,
            f'ksh {s.amount}',
            s.saving_type.name,
            s.date.strftime('%Y-%m-%d')
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 5) Assemble & build document
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response




@login_required(login_url='/user/Login')
@is_user_chama_member
def download_group_saving_report(request, chama_id):
    # 1) Fetch Chama and group Saving data
    chama   = Chama.objects.get(pk=chama_id)
    savings = Saving.objects.filter(chama=chama, forGroup=True)

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_group_savings_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-60,
            "Group Savings Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1]-75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data & style
    data = [[
        'Amount', 'Type', 'Date'
    ]]
    for s in savings:
        data.append([
            f'ksh {s.amount}',
            s.saving_type.name,
            s.date.strftime('%Y-%m-%d')
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 5) Assemble & build
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response





@login_required(login_url='/user/Login')
@is_user_chama_member
def download_group_contributions_report(request, chama_id):
    # ─────────────────────────────────────────────
    # 1) Fetch & flatten your contribution records
    # ─────────────────────────────────────────────
    chama = Chama.objects.get(pk=chama_id)
    contribution_types = Contribution.objects.filter(chama=chama)
    contributions = []
    for ct in contribution_types:
        contributions.extend(ct.records.all())
    contributions = sorted(
        contributions,
        key=lambda x: x.date_created,
        reverse=True
    )

    # ─────────────────────────────────────────────
    # 2) Prepare HTTP + PDF document
    # ─────────────────────────────────────────────
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_group_contributions_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # ─────────────────────────────────────────────
    # 3) Define header callback (runs on every page)
    # ─────────────────────────────────────────────
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0]/2, letter[1] - 40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0]/2, letter[1] - 60,
            "Group Contributions Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1] - 75,
            datetime.now().strftime("%Y-%m-%d")
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])


    data = [[
        'Member', 'Contribution Type', 'Date',
        'Expected Amount', 'Amount Paid', 'Balance'
    ]]
    for c in contributions:
        data.append([
            c.member.name,
            c.contribution.name,
            c.date_created.strftime('%Y-%m-%d'),
            f'ksh {c.amount_expected}',
            f'ksh {c.amount_paid}',
            f'ksh {c.balance}',
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

  
    story = [
        Spacer(1, 40),  # gives some space below header
        table
    ]
    doc.build(story)
    return response

@login_required(login_url='/user/Login')
@is_user_chama_member
def download_member_contribution_report(request, chama_id, member_id):
    # 1) Retrieve Chama and Member
    chama  = Chama.objects.get(pk=chama_id)
    member = ChamaMember.objects.get(pk=member_id)

    # 2) Collect this member's contributions
    contribution_types = Contribution.objects.filter(chama=chama)
    contributions = []
    for ctype in contribution_types:
        for contrib in ctype.records.all():
            if contrib.member == member:
                contributions.append(contrib)

    # 3) Prepare PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_{member.name}_contribution_report.pdf"'
    )

    # 4) Setup BaseDocTemplate with header on each page
    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # Header callback
    def draw_header(canvas, doc):
        canvas.saveState()
        # Title line
        canvas.setFont('Times-Bold', 14)
        canvas.drawCentredString(
            letter[0]/2, letter[1] - 40,
            f"Member Contribution Report - {member.name}"
        )
        # Date line
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0]/2, letter[1] - 55,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 5) Build table data
    data = [[
        'Name', 'Contribution Type', 'Date',
        'Expected Amount', 'Amount Paid', 'Balance'
    ]]
    for contrib in contributions:
        data.append([
            contrib.member.name,
            contrib.contribution.name,
            contrib.date_created.strftime('%Y-%m-%d'),
            f'ksh {contrib.amount_expected}',
            f'ksh {contrib.amount_paid}',
            f'ksh {contrib.balance}'
        ])

    # 6) Create table with repeating header row
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 7) Build story
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)
    return response



@login_required(login_url='/user/Login')
@is_user_chama_member
def download_collected_fine_report(request, chama_id):
    # 1) Fetch Chama and cleared fines
    chama = Chama.objects.get(pk=chama_id)
    # Pull all fines with status 'cleared' in a single queryset
    fines = FineItem.objects.filter(fine_type__chama=chama, status='cleared')

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_collected_fines_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        # Main title
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        # Subtitle and date
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "Collected Fines Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data
    data = [[
        'Member', 'Type', 'Amount', 'Paid Amount',
        'Balance', 'Status', 'Created', 'Last Updated'
    ]]
    for fine in fines:
        data.append([
            fine.member.name,
            fine.fine_type.name,
            f'ksh {fine.fine_amount}',
            f'ksh {fine.paid_fine_amount}',
            f'ksh {fine.fine_balance}',
            fine.status,
            fine.created.strftime('%Y-%m-%d'),
            fine.last_updated.strftime('%Y-%m-%d')
        ])

    # 5) Create table with header row repeated
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 6) Assemble and build document
    story = [
        Spacer(1, 40),  # space below header
        table
    ]
    doc.build(story)
    return response




@login_required(login_url='/user/Login')
@is_user_chama_member
def download_uncollected_fines_report(request, chama_id):
    # 1) Fetch Chama and active fines
    chama = Chama.objects.get(pk=chama_id)
    fines = FineItem.objects.filter(fine_type__chama=chama, status='active')

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_uncollected_fines_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "Uncollected Fines Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data
    data = [[
        'Member', 'Type', 'Amount', 'Paid Amount',
        'Balance', 'Status', 'Created', 'Last Updated'
    ]]
    for fine in fines:
        data.append([
            fine.member.name,
            fine.fine_type.name,
            f'ksh {fine.fine_amount}',
            f'ksh {fine.paid_fine_amount}',
            f'ksh {fine.fine_balance}',
            fine.status,
            fine.created.strftime('%Y-%m-%d'),
            fine.last_updated.strftime('%Y-%m-%d')
        ])

    # 5) Create table with header row repeated
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 6) Assemble and build document
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)
    return response


    


@login_required(login_url='/user/Login')
@is_user_chama_member
def download_cashflow_report(request, chama_id):
    # 1) Fetch Chama and Cashflow Report data
    chama = Chama.objects.get(pk=chama_id)
    reports = CashflowReport.objects.filter(chama=chama).order_by('-date_created')

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{chama.name}_cashflow_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "Cashflow Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data
    data = [['Member', 'Type', 'Amount', 'Date Created']]
    for report in reports:
        member_name = report.member.name if report.member else 'Group'
        data.append([
            member_name,
            report.type,
            f'ksh {report.amount}',
            report.object_date.strftime('%Y-%m-%d')
        ])

    # 5) Create table with header row repeated
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 6) Assemble and build document
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)
    return response



@login_required(login_url='/user/Login')
@is_user_chama_member
def download_member_cashflow_report(request, chama_id, member_id):
    # 1) Fetch Chama, Member, and Cashflow Report data
    chama  = Chama.objects.get(pk=chama_id)
    member = ChamaMember.objects.get(pk=member_id)
    reports = CashflowReport.objects.filter(chama=chama, member=member).order_by('-date_created')

    # 2) Prepare PDF response & BaseDocTemplate
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{member.name}_cashflow_report.pdf"'
    )

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            f"{member.name} Cashflow Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Build table data
    data = [['Member', 'Type', 'Amount', 'Date Created']]
    for report in reports:
        data.append([
            report.member.name,
            report.type,
            f'ksh {report.amount}',
            report.date_created.strftime('%Y-%m-%d')
        ])

    # 5) Create table with header row repeated
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 6) Assemble and build document
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)
    return response


    


@login_required(login_url='/user/Login')
@is_user_chama_member
def download_my_cashflow_report(request, chama_id):
    # 1) Fetch Chama and current user's member record
    chama = Chama.objects.get(pk=chama_id)
    try:
        user_member = chama.member.get(user=request.user)
    except ChamaMember.DoesNotExist:
        return HttpResponse("You are not a member of this chama.", status=403)

    # 2) Fetch Cashflow Reports
    reports = CashflowReport.objects.filter(chama=chama, member=user_member).order_by('-date_created')

    # 3) Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_cashflow_report.pdf"'

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 4) Header callback for every page
    def draw_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "My Cashflow Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 5) Build table data
    data = [['Member', 'Type', 'Amount', 'Date Created']]
    for report in reports:
        data.append([
            report.member.name,
            report.type,
            f'ksh {report.amount}',
            report.date_created.strftime('%Y-%m-%d')
        ])

    # 6) Create and style table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 7) Assemble and build document
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)

    return response

@login_required(login_url='/user/Login')
@is_user_chama_member
def download_expense_report(request, chama_id):
    # 1) Retrieve Chama and expenses
    chama = Chama.objects.get(pk=chama_id)
    expenses = Expense.objects.filter(chama=chama).order_by('-created_on')

    # 2) Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'

    doc = BaseDocTemplate(
        response,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=72, bottomMargin=36
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id='normal'
    )

    # 3) Header callback
    def draw_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 40,
            chama.name
        )
        canvas.setFont('Times-Bold', 12)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 60,
            "Expense Report"
        )
        canvas.setFont('Times-Roman', 10)
        canvas.drawCentredString(
            letter[0] / 2, letter[1] - 75,
            datetime.now().strftime('%Y-%m-%d')
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
    ])

    # 4) Define table data
    data = [['Name', 'Created By', 'Created On', 'Amount']]
    for expense in expenses:
        data.append([
            expense.name,
            expense.created_by.name if expense.created_by else '',
            expense.created_on.strftime('%Y-%m-%d') if expense.created_on else '',
            f'ksh {expense.amount}'
        ])

    # 5) Create and style table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
        ('GRID',         (0, 0), (-1, -1), 1, colors.black),
    ]))

    # 6) Assemble and build document
    story = [
        Spacer(1, 40),
        table
    ]
    doc.build(story)

    return response



#notification handlers
@login_required(login_url='/user/Login')
@is_user_chama_member
def notifications(request,chama_id):
    chama = Chama.objects.get(pk=chama_id)

    if chama:   
        notification_types = NotificationType.objects.filter(chama=chama).all()

        chama_notifications = NotificationItem.objects.filter(chama=chama,forGroup=True,member=None).all()

        member = None
        for member in chama.member.all():
            if request.user == member.user:
                member= member
                break
      

        my_notifications = NotificationItem.objects.filter(member=member,chama=chama,forGroup=False).all()

        context = {
            'types':notification_types,
            'chama_notifs':chama_notifications,
            'my_notifs':my_notifications,
            'members':ChamaMember.objects.filter(active=True,group=chama)
        }
    return render(request,'chamas/notifications.html',context)


@login_required(login_url='/user/Login')
@is_user_chama_member
def create_notif_type(request,chama_id):
    if request.method == 'POST':
        try:
            chama = Chama.objects.get(pk=chama_id)

            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description')

            new_type = NotificationType.objects.create(name=name,chama=chama,description=description)

            data = {
                'status':'success',
                'message':'New notification type created succesfully',
                'type':model_to_dict(new_type)
            }
            return JsonResponse(data,status=200)

        except Exception as e:
            data = {
                'status':'failed',
                'message':f'An error occured:{e}'
            }

            return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'Invalid http method'
        }

        return JsonResponse(data,status=405)


@login_required(login_url='/user/Login')
@is_user_chama_member
def create_notif(request,chama_id):
    if request.method == 'POST':
        try:
            chama = Chama.objects.get(pk=chama_id)

            data = json.loads(request.body)
            member = data.get('member')
            message = str(data.get('message'))
            type = NotificationType.objects.get(pk=int(data.get('type')))

            if member == 'group':
                forGroup = True
                new_notif = NotificationItem.objects.create(
                forGroup = forGroup,
                message=message,
                type=type,
                chama=chama
            )
            else:
                forGroup = False

                try:
                    member = ChamaMember.objects.get(pk=int(member),group=chama)

                except Exception as e:
                    print(e)


                new_notif = NotificationItem.objects.create(
                member= member,
                message=message,
                type=type,
                chama=chama,
                forGroup=forGroup
            )
                
            
            data = {
                'status':'success',
                'message':'Notification sent succesfully',
                'notification':model_to_dict(new_notif)
            }

            return JsonResponse(data,status=200)
        except Exception as e:
            data = {
                'status':'failed',
                'message':f'An error occurred:{e}'
            }

            return JsonResponse(data,status=200)
    else:
        data = {
            'status':'failed',
            'message':'invalid http method'
        }

        return JsonResponse(data,status=405)


