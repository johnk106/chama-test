from django.conf import settings
from pyfcm import FCMNotification
from .models import *
from twilio.rest import Client
import datetime



def notify_single_device(fcm_token, title, message, data):
    try:
        print("im here at notify single device")
        push_service = FCMNotification(api_key='AAAApuuyOe4:APA91bFVU7guIWu7NXlMjndp7s3MjY2u3z9SQRLhrHDljcBfdYk87Bj4aPdxIOEl_1Y14MuaTd4FtQ74LBXvRGT625o071FGoTgGYRcCpB67-m8sfuL4DDr6Cka1BNtuLrDaA4Dex6Ko')
        print(push_service.notify_single_device(
            registration_id=fcm_token,
            message_title=title,
            message_body=message,
            data_message=data
        ))
        return push_service.notify_single_device(
            registration_id=fcm_token,
            message_title=title,
            message_body=message,
            data_message=data
        )
    except:
        print("in except at notify single device")
        return {
            "success": 0
        }


def notify_multiple_devices(fcm_tokens, title, message, data):
    try:
        print("im here at notify multiple device")
        push_service = FCMNotification(api_key='AAAApuuyOe4:APA91bFVU7guIWu7NXlMjndp7s3MjY2u3z9SQRLhrHDljcBfdYk87Bj4aPdxIOEl_1Y14MuaTd4FtQ74LBXvRGT625o071FGoTgGYRcCpB67-m8sfuL4DDr6Cka1BNtuLrDaA4Dex6Ko')
        return push_service.notify_multiple_devices(
            registration_ids=fcm_tokens,
            message_title=title,
            message_body=message,
            data_message=data
        )
    except:
        print("in except at notify multiple device")
        return {
            "success": 0
        }

def send_sms(mobile_number, title,message):
    # print("send sms is called")
    print('line 50 from utils.py message sent on: ',mobile_number)

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #response = client.messages.create(body='Message :' + title+message,to=mobile_number, from_=settings.TWILIO_PHONE_NUMBER)
    return None

def send_notif(fcm_token, mobile_number, send_message, send_notif, title, message, data, multi_user,user):
    if multi_user:
        if send_message and send_notif:
            # Add send message funtionality
            # send_sms(mobile_number, title, message)
            UserNotificationHistory.objects.create(user=user, notification_title=title, notification_body=message
                                                   )

            #notify_multiple_devices(fcm_token, title, message, data)

        elif send_message:
            # send_sms(mobile_number, title,message)
            pass
        else:
            UserNotificationHistory.objects.create(user=user, notification_title=title, notification_body=message
                                                   )
            #notify_multiple_devices(fcm_token, title, message, data)

    else:
        if send_message and send_notif:
            # send_sms(mobile_number, title,message)
            UserNotificationHistory.objects.create(user=user, notification_title=title, notification_body=message
                                                   )
            #notify_single_device(fcm_token, title, message, data)
        elif send_message:
            # send_sms(mobile_number, title,message)
            pass
        else:
            UserNotificationHistory.objects.create(user=user, notification_title=title, notification_body=message
                                                   )
            #notify_single_device(fcm_token, title, message, data)
