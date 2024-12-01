# import json
# from django.contrib.auth import login, logout
# from django.contrib.auth.models import User
# from django.shortcuts import render, redirect
# import random
# from twilio.rest import Client
# from django.conf import settings
# from django.http import HttpResponse
# # Create your views here.
# from django.contrib import auth, messages
# import http.client
# from notifications.models import UserFcmTokens
# from notifications.utils import send_notif
# from Dashboard.models import *
# from django.conf import settings
# from pyment_withdraw.models import *

# from authentication.models import Gender, Payment_Method, How_did_you_find, Profile

# from notifications.models import *


# def send_otp(mobile, otp):
#     try:

#         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#         response = client.messages.create(
#             body='Your OTP to login at CHAMABORA is :' + otp,
#             to=mobile, from_=settings.TWILIO_PHONE_NUMBER)
#         return '200'
#     except:
#         return '500'


# def Login(request):
#     if request.method == 'POST':
#         search_str = 'fGqD6gdf_shF7h_aFBBwe8:APA91bE2E1FGDtKhHFuzbV4a3C4LjWZ5RUQIufAfFi8VfQL7oXurICOVl2BQVsfaTKug9Fx9jmBbwR68nJzjzNJ_FvDWxtY0vrtowqQ0uymgRMGGRpgB79MF9rCsxlOxsQXE07NH3D-k'
#         Username = request.POST.get('un')
#         Password = request.POST.get('password')
#         user = Profile.objects.filter(NIC_No=Username).first()
#         if user is None:
#             messages.error(request, 'User not found with this NIC')
#             return render(request, 'Login.html')
#         user_logging = auth.authenticate(username=Username, password=Password)

#         if user_logging is not None:
#             if user_logging.is_active:
#                 if Username == '33332222' and Password == 'Chama12345!':
#                     user = auth.authenticate(username=Username, password=Password)
#                     print('line no 47 called')

#                     login(request, user)

#                     return redirect('my_goals')


#                 otp = str(random.randint(1000, 9999))
#                 print('OTP is:',otp)
#                 user.otp = otp
#                 user.save()
#                 mobile = user.phone


#                 res=send_otp(mobile, otp)
#                 print('Response form send opt fun is:', res)
#                 if res == '200':


#                     request.session['mobile'] = mobile
#                     request.session['Username'] = Username
#                     request.session['Password'] = Password
#                     return redirect('login_otp')

#                 else:
#                     user = auth.authenticate(username=Username, password=Password)
#                     print('line no 47 called')

#                     login(request, user)
#                     resp = send_notif(search_str, None, True, True, "Successfully Login",
#                                       "You have successfully logged in to ChamaSpace. Welcome!", None, False, user)
#                     print(resp)
#                     UserFcmTokens.objects.create(user=user, token=search_str)

#                     return redirect('my_goals')



#             else:
#                 messages.error(request, 'Account is not activated')
#         else:
#             messages.warning(request, 'Invalid ID or password')
#             return redirect('Login')



#     return render(request, 'Login.html')


# def login_token(request):
#     if request.method == 'POST':
#         search_str = json.loads(request.body).get('searchText')


#         request.session['search_str'] = search_str

#         return redirect('login_otp')




# def login_otp(request):
#     mobile = request.session['mobile']
#     Username = request.session['Username']
#     Password = request.session['Password']

#     if request.method == 'POST':
#         otp = request.POST.get('2facode')
#         search_str = 'fGqD6gdf_shF7h_aFBBwe8:APA91bE2E1FGDtKhHFuzbV4a3C4LjWZ5RUQIufAfFi8VfQL7oXurICOVl2BQVsfaTKug9Fx9jmBbwR68nJzjzNJ_FvDWxtY0vrtowqQ0uymgRMGGRpgB79MF9rCsxlOxsQXE07NH3D-k'


#         profile = Profile.objects.filter(phone=mobile).first()
#         print('Line no 96 OTP is:', otp, profile.otp)

#         if otp == profile.otp:
#             # user = User.objects.get(id=profile.user.id)
#             user = auth.authenticate(username=Username, password=Password)


#             login(request, user)
#                     # code to save user fcm_token to db

#             resp = send_notif(search_str, None, True, True, "Successfully Login", "You have successfully logged in to ChamaSpace. Welcome!", None, False,user)
#             print(resp)
#             UserFcmTokens.objects.create(user=user, token=search_str)


#             return redirect('my_goals')



#         else:
#             messages.error(request, 'Invalid OTP,please try again')
#             return render(request, 'Login_otp.html')

#     return render(request, 'Login_otp.html')


# def Sign_Up(request):
#     if request.method == 'POST':
#         NIC_Nos = str(request.POST.get('nic_no'))
#         f_name = request.POST.get('fname')
#         l_name = request.POST.get('lname')
#         Phone_no_input = str(request.POST.get('phone_no'))
#         without_zero_cellno = Phone_no_input[1:]
#         Phone_no = '+254' + without_zero_cellno
#         print(Phone_no)
#         Password = request.POST.get('password')

#         username = NIC_Nos

#         try:
#             if not User.objects.filter(username=username).exists():

#                 if not Profile.objects.filter(NIC_No=NIC_Nos):
#                     x = User.objects.create_user(first_name=f_name, last_name=l_name,
#                                                  password=Password, username=username)

#                     y = Profile.objects.create(owner=x, NIC_No=NIC_Nos, phone=Phone_no)



#                     x.save()
#                     y.save()
#                     Wallet.objects.create(user_id=x, available_for_withdraw=0.0, pending_clearence=0.0,
#                                           withdrawal=0.0,
#                                           description='Wallet created on Sign Up').save()
#                     Peer_to_Peer_Wallet.objects.create(user_id=x, available_balance=0.0,
#                                                        description='Peer to Peer wallet created on SignUp').save()
#                     Saving_Wallet.objects.create(user_id=x, available_balance=0.0,
#                                                         description='Saving wallet created on SignUp').save()
#                     UserBankDetails.objects.create(user_id=x).save()

#                     request.session['mobile'] = username
#                     return redirect('Sign_Up2')
#                 else:
#                     messages.info(request,
#                                   'User with similar ID or Phone No already exists ')
#                     return redirect('Sign_up')

#             messages.info(request, 'User with similar ID or Phone No already exists')
#             return redirect('Sign_up')
#         except Exception as e:
#             print('Error during Sign Up is:',e)
#             messages.info(request, 'OPS some error has been occur,please contact admin')
#             return redirect('Sign_up')
#     else:
#         return render(request, 'Sign_Up.html')


# def Sign_Up2(request):
#     username = request.session['mobile']
#     Genders = Gender.objects.all()
#     Payment_Methods = Payment_Method.objects.all()
#     How_did_you_finds = How_did_you_find.objects.all()
#     context = {'Genders': Genders, 'Payment_Methods': Payment_Methods, 'How_did_you_finds': How_did_you_finds}

#     if request.method == 'POST':
#         if len(username) > 0:
#             users = User.objects.get(username=username)

#             user_profile = Profile.objects.get(owner=users)

#             Sex = request.POST.get('Sex')

#             Email = request.POST.get('email')
#             payment_gateway = request.POST.get('payment_gateway')

#             how_find_us = request.POST.get('how_find_us')
#             users.email = Email
#             user_profile.gender = Sex
#             user_profile.payment_method = payment_gateway
#             user_profile.how_did_you_find = how_find_us

#             users.save()
#             user_profile.save()
#             users.is_active = True

#             messages.success(request, 'Account Created Successfully')
#             return redirect('Login')
#         else:
#             messages.success(request, 'User doest not exist,please Sign Up ')
#             return redirect('Sign_up')

#     else:

#         return render(request, 'Sign_Up2.html', context)


# # def Sign_Up3(request):
# #     no_chamas_members=chamas_members.objects.all()
# #     frequency_of_contribution=frequency_of_contri.objects.all()
# #     amount_per_contributions=amount_per_contribution.objects.all()
# #     no_of_cycles=no_of_cycle.objects.all()
# #     Genders = Gender.objects.all()
# #     context = {'Genders': Genders,'no_chamas_members': no_chamas_members, 'frequency_of_contribution': frequency_of_contribution, 'amount_per_contributions': amount_per_contributions,'no_of_cycles':no_of_cycles}
# #     users = User.objects.get(username=username)
# #     print(users)
# #     user_profile = Profile.objects.get(owner=users)
# #     if request.method == 'POST':
# #         Numbers_of_chamas_members = request.POST.get('Numbers_of_chamas_members')
# #         frequency = request.POST.get('frequency')
# #         amount = request.POST.get('amount')
# #         print(amount)
# #         cycle = request.POST.get('cycle')
# #         gender_group = request.POST.get('gender_group')
# #
# #         user_profile.No_of_chamas_memebrs=Numbers_of_chamas_members
# #         user_profile.frequency_of_contribution=frequency
# #         user_profile.amount_per_contribution=amount
# #         user_profile.no_of_cycles=cycle
# #
# #         user_profile.save()
# #         messages.success(request, 'Account Created Successfully')
# #         return redirect('Login')
# #     else:
# #      return render(request, 'Sign_Up3.html',context)


# def Logout(request):
#     logout(request)
#     messages.info(request, 'You have been Logged Out')
#     return redirect('Login')


# def forget_password(request):
#     if request.method == 'POST':
#         Username = request.POST.get('un')

#         user = Profile.objects.filter(NIC_No=Username).first()
#         if user is None:
#             messages.error(request, 'User not found with this NIC')
#             return render(request, 'forget-password.html')

#         otp = str(random.randint(1000, 9999))
#         user.otp = 1234
#         user.save()
#         mobile = user.phone
#         res=send_otp(mobile, otp)
#         print('Response form send opt fun is:', res)
#         if res == '200':

#             request.session['mobile'] = mobile
#             request.session['Username'] = Username

#             return redirect('reset_password')
#         else:
#             messages.success(request, 'Sorry an error occure. Please try again later')
#             return redirect('reset_password')

#     return render(request, 'forget-password.html')


# def reset_password(request):
#     mobile = request.session['mobile']
#     Username = request.session['Username']

#     if request.method == 'POST':
#         otp = request.POST.get('2facode')
#         profile = Profile.objects.filter(phone=mobile).first()

#         if otp == profile.otp:

#             request.session['Username'] = Username
#             messages.success(request, 'Verification code match successfully')
#             return redirect('update_password')

#         else:
#             messages.error(request, 'Invalid OTP,please try again')
#             return render(request, 'forget-password.html')

#     return render(request, 'reset_password_otp.html')


# def update_password(request):
#     Username = request.session['Username']

#     if request.method == 'POST':
#         users = User.objects.get(username=Username)
#         print(users)
#         new_password = request.POST.get('new_password')

#         if len(new_password) != 0:
#             users.set_password(new_password)
#             users.save()

#             messages.info(request, 'Password updated successfully,Please Login with New Set Password')
#             return redirect('Login')

#     else:

#         return render(request, 'update_password.html')


# def showFirebaseJS(request):
#     data = 'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
#            'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
#            'var firebaseConfig = {' \
#            '        apiKey: "AIzaSyBHYZJCR9UqOqmDM0YOtEVi9WhoVfNg2eU",' \
#            '        authDomain: "chamabora-b72ce.firebaseapp.com",' \
#            '        databaseURL: "https://chamabora-b72ce-default-rtdb.firebaseio.com/",' \
#            '        projectId: "chamabora-b72ce",' \
#            '        storageBucket: "chamabora-b72ce.appspot.com",' \
#            '        messagingSenderId: "716918897134",' \
#            '        appId: "1:716918897134:web:be99ac855e0d585341b6ff",' \
#            '        measurementId: "${config.measurementId}"' \
#            ' };' \
#            'firebase.initializeApp(firebaseConfig);' \
#            'const messaging=firebase.messaging();' \
#            'messaging.setBackgroundMessageHandler(function (payload) {' \
#            '    console.log(payload);' \
#            '    const notification=JSON.parse(payload);' \
#            '    const notificationOption={' \
#            '        body:notification.body,' \
#            '        icon:notification.icon' \
#            '    };' \
#            '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
#            '});'

#     return HttpResponse(data, content_type="text/javascript")







import json
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
import random
from twilio.rest import Client
from django.conf import settings
from django.http import HttpResponse
# Create your views here.
from django.contrib import auth, messages
import http.client
from notifications.models import UserFcmTokens
from notifications.utils import send_notif
from Dashboard.models import *
from django.conf import settings
from pyment_withdraw.models import *
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import Profile

from authentication.models import Gender, Payment_Method, How_did_you_find, Profile

from notifications.models import *



import http.client
import json




def send_otp(mobile, otp):
    try:

        if mobile[0]=='+':
            mobile=mobile[1:]

        base_url = f"{settings.INFOBIP_API_BASE_URL}"  # Replace with your Infobip base URL
        endpoint = "/whatsapp/1/message/template"
        headers = {
            "Authorization": f"App {settings.INFOBIP_API_KEY}",  
            "Content-Type": "application/json",
            "Accept": "application/json"
        }   
        
        # Payload with template details
        payload = {
            "messages": [
                       {
                    "from": "254710741263",  # Your registered WhatsApp sender ID
                    "to": mobile,
                    "content": {
                        "templateName": "chamaspace_template",  # Approved template name
                        "templateData": {
                            "body": {
                                "placeholders": [otp]  # Dynamic placeholder values
                            },
                            "buttons": [
                                {
                                    "type": "URL",  # Button type
                                    "parameter": otp  # Example parameter for button
                                }
                            ]
                        },
                        "language": "en_GB"  # Ensure language matches your template
                    }
                }
            ]
        }

        # Send the request to Infobip API
        conn = http.client.HTTPSConnection(base_url)
        conn.request("POST", endpoint, json.dumps(payload), headers)
        response = conn.getresponse()
        data = response.read()

        # Parse and handle the response
        if response.status == 200:
            response_data = json.loads(data.decode("utf-8"))
            message_status = response_data.get("messages", [{}])[0].get("status", {}).get("groupName")
            if message_status == "DELIVERED":
                print("OTP successfully delivered.")
                return "200"
            elif message_status == "PENDING":
                print("OTP delivery is pending.")
                return "200"
            else:
                print("Failed to deliver OTP:", response_data)
                return "500"
        else:
            print("HTTP Error:", response.status, "Response:", data.decode("utf-8"))
            return "500"

    except Exception as e:
        print("Error sending WhatsApp OTP:", e)
        return "500"




# def Login(request):
#     if request.method == 'POST':
#         search_str = 'fGqD6gdf_shF7h_aFBBwe8:APA91bE2E1FGDtKhHFuzbV4a3C4LjWZ5RUQIufAfFi8VfQL7oXurICOVl2BQVsfaTKug9Fx9jmBbwR68nJzjzNJ_FvDWxtY0vrtowqQ0uymgRMGGRpgB79MF9rCsxlOxsQXE07NH3D-k'
#         Username = request.POST.get('un')
#         Password = request.POST.get('password')
#         user = Profile.objects.filter(NIC_No=Username).first()
#         if user is None:
#             messages.error(request, 'User not found with this NIC')
#             return render(request, 'Login.html')
#         user_logging = auth.authenticate(username=Username, password=Password)

#         if user_logging is not None:
#             print("come here in 422")
#             if user_logging.is_active:
#                 if Username == '33332222' and Password == 'Chama12345!':
#                     user = auth.authenticate(username=Username, password=Password)
#                     print('line no 47 called')

#                     login(request, user)

#                     return redirect('my_goals')


#                 # otp = str(random.randint(1000, 9999))
#                 # print('OTP is:',otp)
#                 # user.otp = otp
#                 # user.save()
#                 # mobile = user.phone


#                 # res=send_otp(mobile, otp)
#                 # print('Response form send opt fun is:', res)
#                 # if res == '200':


#                 # request.session['mobile'] = mobile
#                 # request.session['Username'] = Username
#                 # request.session['Password'] = Password
#                 # return redirect('login_otp')

#                 # else:
#                 #     user = auth.authenticate(username=Username, password=Password)
#                 #     print('line no 47 called')
#                 print("going to req")
#                 login(request, user)
#                 print("back from req")
#                 resp = send_notif(search_str, None, True, True, "Successfully Login",
#                                     "You have successfully logged in to ChamaSpace. Welcome!", None, False, user)
#                 print("response is",resp)
#                 UserFcmTokens.objects.create(user=user, token=search_str)

#                 return redirect('my_goals')



#             else:
#                 messages.error(request, 'Account is not activated')
#         else:
#             messages.warning(request, 'Invalid ID or password')
#             return redirect('Login')



#     return render(request, 'Login.html')

def Login(request):
    if request.method == 'POST':
        try:
            Username = request.POST.get('un')
            Password = request.POST.get('password')
            user = Profile.objects.filter(NIC_No=Username).first()
            if user is None:
                messages.error(request, 'User not found with this NIC')
                return render(request, 'Login.html')
            
            user_logging = authenticate(username=Username, password=Password)
            if user_logging is not None:
                if user_logging.is_active:
                    login(request, user_logging)
                    return redirect('my_goals')
                else:
                    messages.error(request, 'Account is not activated')
            else:
                messages.warning(request, 'Invalid ID or password')
                return redirect('Login')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return render(request, 'Login.html')

    return render(request, 'Login.html')


def login_token(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')


        request.session['search_str'] = search_str

        return redirect('login_otp')




def login_otp(request):
    mobile = request.session['mobile']
    Username = request.session['Username']
    Password = request.session['Password']

    if request.method == 'POST':
        otp = request.POST.get('2facode')
        search_str = 'fGqD6gdf_shF7h_aFBBwe8:APA91bE2E1FGDtKhHFuzbV4a3C4LjWZ5RUQIufAfFi8VfQL7oXurICOVl2BQVsfaTKug9Fx9jmBbwR68nJzjzNJ_FvDWxtY0vrtowqQ0uymgRMGGRpgB79MF9rCsxlOxsQXE07NH3D-k'


        profile = Profile.objects.filter(phone=mobile).first()
        print('Line no 96 OTP is:', otp, profile.otp)

        if otp == profile.otp:
            # user = User.objects.get(id=profile.user.id)
            user = auth.authenticate(username=Username, password=Password)


            login(request, user)
                    # code to save user fcm_token to db

            resp = send_notif(search_str, None, True, True, "Successfully Login", "You have successfully logged in to ChamaSpace. Welcome!", None, False,user)
            print(resp)
            UserFcmTokens.objects.create(user=user, token=search_str)


            return redirect('my_goals')



        else:
            messages.error(request, 'Invalid OTP,please try again')
            return render(request, 'Login_otp.html')

    return render(request, 'Login_otp.html')


# def Sign_Up(request):
#     if request.method == 'POST':
#         NIC_Nos = str(request.POST.get('nic_no'))
#         f_name = request.POST.get('fname')
#         l_name = request.POST.get('lname')
#         Phone_no_input = str(request.POST.get('phone_no'))
#         without_zero_cellno = Phone_no_input[1:]
#         Phone_no = '+254' + without_zero_cellno
#         print(Phone_no)
#         Password = request.POST.get('password')

#         username = NIC_Nos

#         try:
#             if not User.objects.filter(username=username).exists():

#                 if not Profile.objects.filter(NIC_No=NIC_Nos):
#                     x = User.objects.create_user(first_name=f_name, last_name=l_name,
#                                                  password=Password, username=username)

#                     y = Profile.objects.create(owner=x, NIC_No=NIC_Nos, phone=Phone_no)



#                     x.save()
#                     y.save()
#                                         # Send OTP here after user successfully registers
#                     otp = str(random.randint(1000, 9999))
#                     print("Generated OTP for SignUp:", otp)
#                     y.otp = otp  # Save OTP in the profile
#                     y.save()

#                     # Send OTP to the user's phone number
#                     res = send_otp(Phone_no, otp)
#                     if res == '200':
#                         request.session['mobile'] = Phone_no
#                         request.session['Username'] = username
#                         return redirect('verify_otp')  # Redirect to OTP verification page
#                     else:
#                         messages.error(request, 'Failed to send OTP. Please try again later.')
#                         return redirect('Sign_up')

#                     Wallet.objects.create(user_id=x, available_for_withdraw=0.0, pending_clearence=0.0,
#                                           withdrawal=0.0,
#                                           description='Wallet created on Sign Up').save()
#                     Peer_to_Peer_Wallet.objects.create(user_id=x, available_balance=0.0,
#                                                        description='Peer to Peer wallet created on SignUp').save()
#                     Saving_Wallet.objects.create(user_id=x, available_balance=0.0,
#                                                         description='Saving wallet created on SignUp').save()
#                     UserBankDetails.objects.create(user_id=x).save()

#                     request.session['mobile'] = username
#                     return redirect('Sign_Up2')
#                 else:
#                     messages.info(request,
#                                   'User with similar ID or Phone No already exists ')
#                     return redirect('Sign_up')

#             messages.info(request, 'User with similar ID or Phone No already exists')
#             return redirect('Sign_up')
#         except Exception as e:
#             print('Error during Sign Up is:',e)
#             messages.info(request, 'OPS some error has been occur,please contact admin')
#             return redirect('Sign_up')
#     else:
#         return render(request, 'Sign_Up.html')




def Sign_Up(request):
    if request.method == 'POST':
        try:
            NIC_Nos = str(request.POST.get('nic_no'))
            f_name = request.POST.get('fname')
            l_name = request.POST.get('lname')
            Phone_no_input = str(request.POST.get('phone_no'))
            without_zero_cellno = Phone_no_input[1:]
            Phone_no = '+254' + without_zero_cellno
            Password = request.POST.get('password')

            # Check if NIC or phone already exists
            if User.objects.filter(username=NIC_Nos).exists() or Profile.objects.filter(NIC_No=NIC_Nos).exists():
                messages.error(request, 'User with similar ID or Phone No already exists')
                return redirect('Sign_up')

            # Generate OTP and save to session
            otp = str(random.randint(1000, 9999))
            print("Generated OTP for SignUp:", otp)
            res = send_otp(Phone_no, otp)

            if res == '200':
                # Store temporary data in the session
                request.session['signup_data'] = {
                    'nic_no': NIC_Nos,
                    'fname': f_name,
                    'lname': l_name,
                    'phone_no': Phone_no,
                    'password': Password,
                    'otp': otp
                }
                return redirect('verify_otp')  # Redirect to OTP verification page
            else:
                messages.error(request, 'Failed to send OTP. Please try again later.')
                return redirect('Sign_up')
        except Exception as e:
            print('Error during Sign Up:', e)
            messages.error(request, 'An error occurred during sign-up. Please try again.')
            return redirect('Sign_up')
    else:
        return render(request, 'Sign_Up.html')


def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_data = request.session.get('signup_data')

        if not session_data:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect('Sign_up')

        # Validate OTP
        if user_otp == session_data['otp']:
            try:
                # Create user and profile after OTP verification
                x = User.objects.create_user(
                    first_name=session_data['fname'],
                    last_name=session_data['lname'],
                    username=session_data['nic_no'],
                    password=session_data['password']
                )
                y = Profile.objects.create(owner=x, NIC_No=session_data['nic_no'], phone=session_data['phone_no'])

                # Create wallets and related objects
                Wallet.objects.create(user_id=x, available_for_withdraw=0.0, pending_clearence=0.0,
                                      withdrawal=0.0, description='Wallet created on Sign Up')
                Peer_to_Peer_Wallet.objects.create(user_id=x, available_balance=0.0,
                                                   description='Peer to Peer wallet created on SignUp')
                Saving_Wallet.objects.create(user_id=x, available_balance=0.0,
                                             description='Saving wallet created on SignUp')
                UserBankDetails.objects.create(user_id=x)

                # Clear session and redirect to success page
                del request.session['signup_data']
                messages.success(request, 'Sign up successful. You can now log in.')

                login(request, x)
                return redirect('my_goals')            
            except Exception as e:
                print('Error creating user after OTP verification:', e)
                messages.error(request, 'An error occurred. Please contact support.')
                return redirect('Sign_up')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')
    else:
        return render(request, 'Verify_OTP.html')


def Sign_Up2(request):
    username = request.session['mobile']
    Genders = Gender.objects.all()
    Payment_Methods = Payment_Method.objects.all()
    How_did_you_finds = How_did_you_find.objects.all()
    context = {'Genders': Genders, 'Payment_Methods': Payment_Methods, 'How_did_you_finds': How_did_you_finds}

    if request.method == 'POST':
        if len(username) > 0:
            users = User.objects.get(username=username)

            user_profile = Profile.objects.get(owner=users)

            Sex = request.POST.get('Sex')

            Email = request.POST.get('email')
            payment_gateway = request.POST.get('payment_gateway')

            how_find_us = request.POST.get('how_find_us')
            users.email = Email
            user_profile.gender = Sex
            user_profile.payment_method = payment_gateway
            user_profile.how_did_you_find = how_find_us

            users.save()
            user_profile.save()
            users.is_active = True

            messages.success(request, 'Account Created Successfully')
            return redirect('Login')
        else:
            messages.success(request, 'User doest not exist,please Sign Up ')
            return redirect('Sign_up')

    else:

        return render(request, 'Sign_Up2.html', context)


# def Sign_Up3(request):
#     no_chamas_members=chamas_members.objects.all()
#     frequency_of_contribution=frequency_of_contri.objects.all()
#     amount_per_contributions=amount_per_contribution.objects.all()
#     no_of_cycles=no_of_cycle.objects.all()
#     Genders = Gender.objects.all()
#     context = {'Genders': Genders,'no_chamas_members': no_chamas_members, 'frequency_of_contribution': frequency_of_contribution, 'amount_per_contributions': amount_per_contributions,'no_of_cycles':no_of_cycles}
#     users = User.objects.get(username=username)
#     print(users)
#     user_profile = Profile.objects.get(owner=users)
#     if request.method == 'POST':
#         Numbers_of_chamas_members = request.POST.get('Numbers_of_chamas_members')
#         frequency = request.POST.get('frequency')
#         amount = request.POST.get('amount')
#         print(amount)
#         cycle = request.POST.get('cycle')
#         gender_group = request.POST.get('gender_group')
#
#         user_profile.No_of_chamas_memebrs=Numbers_of_chamas_members
#         user_profile.frequency_of_contribution=frequency
#         user_profile.amount_per_contribution=amount
#         user_profile.no_of_cycles=cycle
#
#         user_profile.save()
#         messages.success(request, 'Account Created Successfully')
#         return redirect('Login')
#     else:
#      return render(request, 'Sign_Up3.html',context)


def Logout(request):
    logout(request)
    messages.info(request, 'You have been Logged Out')
    return redirect('Login')


def forget_password(request):
    if request.method == 'POST':
        try:
            # Get the username (e.g., NIC)
            Username = request.POST.get('un')
            print("Username entered:", Username)

            # Check if user exists
            user = Profile.objects.filter(NIC_No=Username).first()
            if user is None:
                messages.error(request, 'User not found with this NIC.')
                return render(request, 'forget-password.html')

            # Generate a 4-digit OTP
            otp = str(random.randint(1000, 9999))
            print("Generated OTP:", otp)

            # Send OTP to the user's mobile number
            mobile = user.phone
            print("Sending OTP to mobile:", mobile)
            res = send_otp(mobile, otp)

            if res == '200':
                # Store OTP and mobile number in session for validation
                request.session['otp'] = otp
                request.session['mobile'] = mobile
                request.session['Username'] = Username
                messages.success(request, 'Verification code sent successfully!')
                return redirect('reset_password')
            else:
                messages.error(request, 'Failed to send verification code. Please try again later.')
                return render(request, 'forget-password.html')

        except Exception as e:
            print("Error in forget_password:", e)
            messages.error(request, 'An unexpected error occurred. Please try again.')
            return render(request, 'forget-password.html')

    return render(request, 'forget-password.html')

def reset_password(request):
    try:
        # Retrieve session data
        otp_session = request.session.get('otp')
        mobile = request.session.get('mobile')
        Username = request.session.get('Username')

        if not otp_session or not mobile or not Username:
            messages.error(request, 'Session expired. Please try again.')
            return redirect('forget_password')

        if request.method == 'POST':
            otp_entered = request.POST.get('2facode')

            if otp_entered == otp_session:
                messages.success(request, 'Verification code matched successfully!')
                return redirect('update_password')  # Redirect to update password page
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
                return render(request, 'reset_password_otp.html')

    except Exception as e:
        print("Error in reset_password:", e)
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return redirect('forget_password')

    return render(request, 'reset_password_otp.html')


def update_password(request):
    Username = request.session['Username']

    if request.method == 'POST':
        users = User.objects.get(username=Username)
        print(users)
        new_password = request.POST.get('new_password')

        if len(new_password) != 0:
            users.set_password(new_password)
            users.save()

            messages.info(request, 'Password updated successfully,Please Login with New Set Password')
            return redirect('Login')

    else:

        return render(request, 'update_password.html')


def showFirebaseJS(request):
    data = 'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");' \
           'importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js"); ' \
           'var firebaseConfig = {' \
           '        apiKey: "AIzaSyBHYZJCR9UqOqmDM0YOtEVi9WhoVfNg2eU",' \
           '        authDomain: "chamabora-b72ce.firebaseapp.com",' \
           '        databaseURL: "https://chamabora-b72ce-default-rtdb.firebaseio.com/",' \
           '        projectId: "chamabora-b72ce",' \
           '        storageBucket: "chamabora-b72ce.appspot.com",' \
           '        messagingSenderId: "716918897134",' \
           '        appId: "1:716918897134:web:be99ac855e0d585341b6ff",' \
           '        measurementId: "${config.measurementId}"' \
           ' };' \
           'firebase.initializeApp(firebaseConfig);' \
           'const messaging=firebase.messaging();' \
           'messaging.setBackgroundMessageHandler(function (payload) {' \
           '    console.log(payload);' \
           '    const notification=JSON.parse(payload);' \
           '    const notificationOption={' \
           '        body:notification.body,' \
           '        icon:notification.icon' \
           '    };' \
           '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
           '});'

    return HttpResponse(data, content_type="text/javascript")
