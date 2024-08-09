from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mpesa_integration.mpesa_credentials import LipanaMpesaPpassword, MpesaAccessToken
from .models import SubscriptionPlan, ChamaSubscription, PaymentDetail
from django.utils import timezone
from django.urls import reverse
from urllib.parse import urlencode

from notifications.utils import *
from authentication.models import *
from notifications.models import *
from chamas.models import Chama


from datetime import datetime, timedelta
from .utils import generate_jwt, decode_jwt

from django.conf import settings

import requests
import json

PAYMENT_SECRET_KEY = settings.SECRET_KEY


@login_required(login_url='/user/Login')
def subscription_chama(request, chama_id):
    if(chama_id):
        request.session['chama_id'] = chama_id
    return redirect('subscription_plans')


@login_required(login_url='/user/Login')
def subscription_plans(request):
    chama_id = request.session['chama_id']

    plan = SubscriptionPlan.objects.first() 
    chama = Chama.objects.get(id=chama_id)
    plan = SubscriptionPlan.objects.first()
    user = User.objects.filter(username=request.user).first()
    (isTrial, isActive, current_chama_subscription) = is_subscription_active(chama, plan, user)

    print(chama_id)

    return render(request, 'subscriptions/plans.html', {
        'plan': plan,
        'is_trial': isTrial,
        'is_active': isActive,
        'chama_id': chama_id,
        'current_chama_subscription': current_chama_subscription,
        'expiration_date': current_chama_subscription.end_date if current_chama_subscription else None,
    })


@login_required(login_url='/user/Login')
def start_trial(request):
    chama_id = request.session.get('chama_id')
    chama = Chama.objects.get(id=chama_id)
    plan = SubscriptionPlan.objects.first()
    active_subscription_exists = ChamaSubscription.objects.filter(
        chama=chama,
        user=request.user,
        end_date__gt=timezone.now()
    ).exists()
    user = User.objects.filter(username=request.user).first()
    if not active_subscription_exists:
        trial_subscription = ChamaSubscription(
            chama=chama,
            user=user,
            plan=plan,
            start_date=timezone.now(),
            end_date=timezone.now() + plan.trial_duration
        )
        trial_subscription.save()
    return redirect('chamas:chama-dashboard', chama_id=chama_id)

@login_required(login_url='/user/Login')
def subscribe(request):
    profile = Profile.objects.filter(owner=request.user).first()

    if(request.session['chama_id']):
        request.session['chama_id'] = request.session['chama_id']

    chama_id = request.session['chama_id']

    chama = Chama.objects.get(id=chama_id)
    plan = SubscriptionPlan.objects.first()

    chama_subscription = None
    try:
        chama_subscription = ChamaSubscription.objects.filter(
            chama=chama,
            plan=plan
        ).latest('id')
    except ChamaSubscription.DoesNotExist:
        chama_subscription = None  

    if request.method == 'POST':
        if chama and chama_subscription:
            # chama_subscription = chama.chamasubscription
            # chama_subscription.end_date = timezone.now() + plan.trial_duration
            # chama_subscription.save()
            pass
        else:
            chama_subscription = ChamaSubscription.objects.create(
                end_date=timezone.now() + plan.trial_duration,
                chama=chama,
                plan=plan
            )
            chama_subscription.save()
         
        return redirect('subscription_success')

    plan_price = float(plan.price) 
    tax = plan_price * 0.16
    total_amount = plan_price
    amount = total_amount - tax

    return render(request, 'subscriptions/subscribe.html', {
        'plan': plan,
        'phone': profile.phone,
        'chama_id': chama_id,
        'user_id': request.user,
        'plan_id': plan.id,

        'receipt_amount': amount, 
        'receipt_tax': tax, 
        'receipt_total_amount': total_amount
    })


def lipa_na_mpesa_online(chama_id, user_id, plan_id, phone, amount:int):
    without_plus_cellno = phone[1:]
    phone = int(''.join(filter(str.isdigit, without_plus_cellno)))

    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    computed_signature = generate_jwt({
        'chama_id':chama_id, 
        'user_id':user_id, 
        'plan_id':plan_id,
        'phone':phone,
        'amount':amount
    }, PAYMENT_SECRET_KEY)
    
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone,  # replace with your phone number to get stk push
        "CallBackURL": f"https://chamaspace.com/subscriptions/webhook/{computed_signature}",
        "AccountReference": "chamaspace software",
        "TransactionDesc": "chamabora stk push"
    }

    print(request)

    response = requests.post(api_url, json=request, headers=headers)
    data = response.json()

    success = data['ResponseCode'] == "0"
    message = data.get('ResponseDescription', 'Unknown error occurred.')

    if not success:
        if data['ResponseCode'] == "1":
            message = "Insufficient funds. Please top up your M-Pesa account."
        elif data['ResponseCode'] == "2":
            message = "M-Pesa service is currently unavailable. Please try again later."
        
    return {
        'success' : success,
        'message' : message,
        'signature' : computed_signature
    }


def is_subscription_active(chama, plan, user):
    try:
        current_chama_subscription = ChamaSubscription.objects.filter(
            end_date__gte=timezone.now(), 
            chama=chama,
            plan=plan,
            user=user,
        ).latest('end_date')
    except ChamaSubscription.DoesNotExist:
        return (False, None, None)
    
    isTrial = current_chama_subscription.is_trial()
    isActive = current_chama_subscription.is_active()

    return (isTrial, isActive, current_chama_subscription)


    # if current_chama_subscription.end_date > timezone.now():
    #     return (True, current_chama_subscription, current_chama_subscription.end_date)
    # else:
    #     return (False, current_chama_subscription, current_chama_subscription.end_date)
    
# def is_subscription_active(chama, plan, user):
#     try:
#         current_chama_subscription = ChamaSubscription.objects.filter(
#             end_date__gte=timezone.now(), 
#             chama=chama,
#             plan=plan,
#             user=user,
#         ).latest('end_date')
#     except ChamaSubscription.DoesNotExist:
#         return (False, None)

#     if current_chama_subscription.end_date > timezone.now():
#         return (True, current_chama_subscription)
#     else:
#         return (False, None)

def add_subscription(chama:Chama, user:User, plan:SubscriptionPlan, payment_details:PaymentDetail, current_chama_subscription:ChamaSubscription, phone:str, active:bool):
    remaining_days = 0
    
    if current_chama_subscription and active:
        _remaining_days = current_chama_subscription.end_date - timezone.now()
        remaining_days = max(_remaining_days.days, 0)

    chama_subscription = ChamaSubscription.objects.create(
        end_date=timezone.now() + timedelta(days=remaining_days + 30),
        chama=chama,
        plan=plan,
        user=user,
        phone=phone,
        payment_details=payment_details
    )

    chama_subscription.save()


def parse_mpesa_info(payload:dict):
    try:
        callback = payload.get('Body', {}).get('stkCallback', {})
        result_code = callback.get('ResultCode')
        result_desc = callback.get('ResultDesc')
        metadata = callback.get('CallbackMetadata', {}).get('Item', [])
        
        payment_details = {
            "Amount": None,
            "MpesaReceiptNumber": None,
            "TransactionDate": None,
            "PhoneNumber": None,
            "ResultDesc": None
        }

        payment_details['ResultDesc'] = result_desc

        for item in metadata:
            if item.get('Name') == 'Amount':
                payment_details['Amount'] = item.get('Value')
            elif item.get('Name') == 'MpesaReceiptNumber':
                payment_details['MpesaReceiptNumber'] = item.get('Value')
            elif item.get('Name') == 'TransactionDate':
                transaction_date_str = str(item.get('Value'))
                transaction_date = datetime.strptime(transaction_date_str, '%Y%m%d%H%M%S')
                payment_details['TransactionDate'] = transaction_date
            elif item.get('Name') == 'PhoneNumber':
                payment_details['PhoneNumber'] = item.get('Value')

        print("Payment details:", payment_details)

        return (payment_details, None)
        
    except json.JSONDecodeError:
        return (None, "Invalid JSON payload")
    


@csrf_exempt
def subscription_webhook(request, signature):
    #chama_id, user_id, plan_id, 
    if request.method == 'POST':
        if not signature:
            return HttpResponseForbidden('Missing signature query parameter')
    
        payload = json.loads(request.body)
        print("Received payload:", payload)
        
        decoded_payload = decode_jwt(signature, PAYMENT_SECRET_KEY)

        # verify the webhook with a signature
        if not decoded_payload:
            return HttpResponseForbidden('Invalid signature')
        
        chama_id = decoded_payload.get('chama_id')
        user_id = decoded_payload.get('user_id')
        plan_id = decoded_payload.get('plan_id')

        chama = Chama.objects.get(id=chama_id)
        plan = SubscriptionPlan.objects.first()
        user = User.objects.filter(username=user_id).first()

        (isTrial, isActive, current_chama_subscription) = is_subscription_active(chama, plan, user)

        (mpesa_response, error) = parse_mpesa_info(payload)

        payment_detail_data = {
            'amount': mpesa_response['Amount'],
            'mpesa_receipt_number': mpesa_response['MpesaReceiptNumber'],
            'transaction_date': mpesa_response['TransactionDate'],
            'phone_number': mpesa_response['PhoneNumber'],
            'result_desc': mpesa_response['ResultDesc'],
            'payment_status': "SUCCESS",
            'possible_duplicate': isActive,  # Assuming isActive is defined elsewhere
        }
        payment_details = PaymentDetail.objects.create(**payment_detail_data)

        if not error and not isActive:
            add_subscription(chama, user, plan, payment_details, current_chama_subscription, mpesa_response['PhoneNumber'], isActive)
    
    return HttpResponse('Webhook received')





@login_required(login_url='/user/Login')
@csrf_exempt
def subscription_waiting(request, signature = None):
    if request.method == 'POST':
        amount = (float(request.POST.get('amount')))
        phone = request.POST.get('phone')
        user_id = request.POST.get('user_id')
        chama_id = request.POST.get('chama_id')
        plan_id = request.POST.get('plan_id')

        response = lipa_na_mpesa_online(chama_id, user_id, plan_id, phone, amount)
        signature = response.get('signature')

        if response.get('success'):
            redirect_url = reverse('subscription_waiting_with_signature',kwargs={
                'signature' : signature
            }) 
        else:
            query_params = {
                'message' : response.get('message')
            }
            query_string = urlencode(query_params)
            redirect_url = reverse('subscription_error') + '?' + query_string
            
        return redirect(redirect_url)
    else:
        profile = Profile.objects.filter(owner=request.user).first()
        if(request.session['chama_id']):
            request.session['chama_id'] = request.session['chama_id']
        chama_id = request.session['chama_id']

        return render(request, 'subscriptions/waiting.html', {
            'chama_id': chama_id,
            'signature': signature,
        })
   

@login_required(login_url='/user/Login')
def subscription_status(request, signature = None):
    decoded_payload = decode_jwt(signature, PAYMENT_SECRET_KEY) 
    # print(decoded_payload)

    chama_id = decoded_payload.get('chama_id')
    user_id = decoded_payload.get('user_id')
    plan_id = decoded_payload.get('plan_id')
    amount = decoded_payload.get('amount')
    phone = decoded_payload.get('phone')

    chama = Chama.objects.get(id=chama_id)
    plan = SubscriptionPlan.objects.first()
    # user = User.objects.filter(username=user_id).first()

    chama_subscription = None
    try:
        chama_subscription = ChamaSubscription.objects.filter(
            chama=chama,
            plan=plan
        ).latest('id')
    except ChamaSubscription.DoesNotExist:
        chama_subscription = None  

    if not chama_subscription:
        return
    
    if amount != plan.price:
        return

    try:
        success_payment_details = PaymentDetail.objects.filter(
            amount=amount,
            phone_number=phone,
            payment_status="SUCCESS"
        ).latest("id")
    except PaymentDetail.DoesNotExist:
        success_payment_details = None

    try:
        failed_payment_details = PaymentDetail.objects.filter(
            amount=amount,
            phone_number=phone,
            payment_status="FAILED"
        ).latest("id")
    except PaymentDetail.DoesNotExist:
        failed_payment_details = None

    settled_payment_details = success_payment_details if success_payment_details else failed_payment_details
    settled_payment_details_dict = settled_payment_details.__dict__ if settled_payment_details else None
    settled_payment_details_dict.pop("_state", None)

    message = failed_payment_details.result_desc if failed_payment_details else ''
    message = success_payment_details.result_desc if success_payment_details and message == '' else ''

    return JsonResponse({
        'settled': settled_payment_details_dict,
        'success': bool(success_payment_details) and not bool(failed_payment_details),
        'message': message
    })


@login_required(login_url='/user/Login')
def subscription_success(request):
    if(request.session['chama_id']):
        request.session['chama_id'] = request.session['chama_id']
    chama_id = request.session['chama_id']
    return render(request, 'subscriptions/success.html', {'chama_id': chama_id})



@login_required(login_url='/user/Login')
def subscription_error(request, error = None):
    if(request.session['chama_id']):
        request.session['chama_id'] = request.session['chama_id']
    chama_id = request.session['chama_id']
    return render(request, 'subscriptions/error.html', {
        'chama_id': chama_id,
        'error': error
    })
