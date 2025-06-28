import random
import json
import http.client
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from notifications.models import UserFcmTokens
from notifications.utils import send_notif
from authentication.models import Profile
from Dashboard.models import Wallet, Peer_to_Peer_Wallet, Saving_Wallet
from pyment_withdraw.models import UserBankDetails

class OTPService:
    @staticmethod
    def send_otp(mobile, otp):
        try:
            if mobile.startswith('+'):
                mobile = mobile[1:]
            base_url = settings.INFOBIP_API_BASE_URL
            endpoint = "/whatsapp/1/message/template"
            headers = {
                "Authorization": f"App {settings.INFOBIP_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "messages": [{
                    "from": "254791638574",
                    "to": mobile,
                    "content": {
                        "templateName": "chamaspace_template",
                        "templateData": {"body": {"placeholders": [otp]}, "buttons": [{"type": "URL", "parameter": otp}]},
                        "language": "en_GB"
                    }
                }]
            }
            conn = http.client.HTTPSConnection(base_url)
            conn.request("POST", endpoint, json.dumps(payload), headers)
            response = conn.getresponse()
            data = response.read()
            if response.status == 200:
                resp = json.loads(data.decode())
                status = resp.get("messages", [{}])[0].get("status", {}).get("groupName")
                return "200" if status in ("DELIVERED", "PENDING") else "500"
            return "500"
        except Exception:
            return "500"

    @staticmethod
    def get_profile_by_nic(nic):
        return Profile.objects.filter(NIC_No=nic).first()

    @staticmethod
    def handle_signup(request):
        if request.method == 'POST':
            nic = request.POST.get('nic_no')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            phone = '+254' + request.POST.get('phone_no')[1:]
            password = request.POST.get('password')
            if User.objects.filter(username=nic).exists() or Profile.objects.filter(NIC_No=nic).exists():
                messages.error(request, 'User with similar ID or Phone No already exists')
                return redirect('Sign_up')
            otp = str(random.randint(1000, 9999))
            if OTPService.send_otp(phone, otp) == '200':
                request.session['signup_data'] = {'nic': nic, 'fname': fname, 'lname': lname, 'phone': phone, 'password': password, 'otp': otp}
                return redirect('verify_otp')
            messages.error(request, 'Failed to send OTP')
        return render(request, 'Sign_Up.html')

    @staticmethod
    def verify_signup_otp(request):
        if request.method == 'POST':
            user_otp = request.POST.get('otp')
            data = request.session.get('signup_data')
            if not data:
                messages.error(request, 'Session expired')
                return redirect('Sign_up')
            if user_otp == data['otp']:
                user = User.objects.create_user(first_name=data['fname'], last_name=data['lname'], username=data['nic'], password=data['password'])
                Profile.objects.create(owner=user, NIC_No=data['nic'], phone=data['phone'])
                Wallet.objects.create(user_id=user, available_for_withdraw=0.0, pending_clearence=0.0, withdrawal=0.0, description='Wallet created')
                Peer_to_Peer_Wallet.objects.create(user_id=user, available_balance=0.0, description='P2P wallet created')
                Saving_Wallet.objects.create(user_id=user, available_balance=0.0, description='Saving wallet created')
                UserBankDetails.objects.create(user_id=user)
                del request.session['signup_data']
                login(request, user)
                return redirect('Sign_Up2')
            messages.error(request, 'Invalid OTP')
        return render(request, 'Verify_OTP.html')

    @staticmethod
    def verify_login_otp(request):
        if request.method == 'POST':
            otp = request.POST.get('2facode')
            mobile = request.session.get('mobile')
            data = request.session
            profile = Profile.objects.filter(phone=mobile).first()
            if otp == profile.otp:
                user = authenticate(username=data['Username'], password=data['Password'])
                login(request, user)
                token = data['search_str']
                send_notif(token, None, True, True, "Successfully Login", "Welcome!", None, False, user)
                UserFcmTokens.objects.create(user=user, token=token)
                return redirect('my_goals')
            messages.error(request, 'Invalid OTP')
        return render(request, 'Login_otp.html')