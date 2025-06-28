from bot.models import *
from django.conf import settings
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from chamas.models import *
from authentication.models import Profile
from django.db import IntegrityError
from django.http import JsonResponse
import requests



class MemberService:
    INFOBIP_API_KEY   = settings.INFOBIP_API_KEY
    INFOBIP_SENDER_ID = settings.INFOBIP_SENDER_ID     
    INFOBIP_BASE_URL  = "https://api.infobip.com"

    def process_member(self,message,sender):
        name = message['name']
        email = message['email']
        id_number = message['id_number']
        phone = message['phone']
        role = message['role'].lower()
        chama_name = message['chama']

        terms = chama_name.strip().split()
        q = Q()
        for term in terms:
            q &= Q(name__icontains=term)
        chamas = Chama.objects.filter(q)
        if not chamas.exists():
            return self.send_message(f"No chama found matching '{chama_name}'",sender)
        
        if chamas.count() > 1:
            return self.send_message(f"Multiple chamas match the submitted name,please add the user manually",sender)
        
        chama = chamas.first()

        role = Role.objects.filter(name = str(role)).first()
        if not role:
            return self.send_message("Submitted role is not valid,please submit a valid role",sender)
        
        user = User.objects.filter(username=id_number).first()

        existing_member = ChamaMember.objects.filter(group=chama,member_id=id_number).first()
        if existing_member:
            return self.send_message("Member with that ID already exists in  this chama",sender)

        try:
            if user:
                profile = Profile.objects.get(owner=user)

                new_member = ChamaMember.objects.create(
                    name = user.first_name + ' ' + user.last_name,
                    email = user.email,
                    mobile = profile.phone,
                    group = chama,
                    role = role,
                    user=user,
                    profile=profile.picture,
                    member_id=id_number
                )
            else:
                new_member = ChamaMember.objects.create(
                    name = name,
                    mobile=phone,
                    email=email,
                    group=chama,
                    role=role,
                    member_id=id_number
                )
            new_bot_member = BotMember.objects.create(
                name=name,
                email=email,
                id_number=id_number,
                phone=phone,
                role=role,
                chama_name=chama.name,
                member=new_member,
                chama=chama,
                sender=sender
            )

            return self.send_message(f"New member with id {id_number} succesfully added to chama '{chama.name}'",sender)

        except IntegrityError:
            return self.send_message(f"Member with that ID already exists in chama '{chama_name}'",sender)
        
        except:
            return self.send_message(f'An error occured during member creation,please try again.',sender)
    @staticmethod
    def send_message(text, to):
        print(to)
        to_digits = "".join(filter(str.isdigit, to))

        url = f"{MemberService.INFOBIP_BASE_URL}/whatsapp/1/message/text"
        headers = {
            "Authorization": f"App {MemberService.INFOBIP_API_KEY}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

        payload = {
            "from": MemberService.INFOBIP_SENDER_ID,
            "to":   to_digits,
            "content": {
                "text": text
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload)
        except Exception as e:
            return JsonResponse(
                {"error": "Exception during send_message", "details": str(e)},
                status=502
            )

        if 200 <= resp.status_code < 300:
            return JsonResponse(
                {"status": "message_sent", "to": to_digits},
                status=200
            )
        else:
            return JsonResponse(
                {
                    "error":   "Failed to send message",
                    "status":  resp.status_code,
                    "details": resp.text
                },
                status=502
            )



