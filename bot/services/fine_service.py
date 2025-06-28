from bot.models import *
from django.conf import settings
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.http import JsonResponse
import requests

class FineService:
    INFOBIP_API_KEY   = settings.INFOBIP_API_KEY
    INFOBIP_SENDER_ID = settings.INFOBIP_SENDER_ID     
    INFOBIP_BASE_URL  = "https://api.infobip.com"

    def process_fine(self, message, sender):
        member_id  = message['member_id']
        amount     = Decimal(message['amount'])
        chama_name = message['chama_name']

        terms = chama_name.strip().split()
        q = Q()
        for term in terms:
            q &= Q(name__icontains=term)
        chamas = Chama.objects.filter(q)
        if not chamas.exists():
            return self.send_message(f"No chama found matching '{chama_name}'", sender)
        if chamas.count() > 1:
            chamas = chamas.filter(chamamember__member_id=member_id).distinct()
            if not chamas.exists():
                return self.send_message(
                    f"Multiple chamas match '{chama_name}' but none have member '{member_id}'",
                    sender
                )
        chama = chamas.first()

        member = ChamaMember.objects.filter(member_id=member_id, group=chama).first()
        if not member:
            admin_role = Role.objects.filter(name='admin').first()
            admin = ChamaMember.objects.filter(group=chama,role=admin_role).first()

            if admin.user.username != member_id:
                return self.send_message("Member not found in the chama", sender)
            
            else:
                member = admin

        fine = (
            FineItem.objects
            .filter(member=member, fine_balance__gt=0, fine_type__chama=chama)
            .order_by('created')
            .first()
        )
        if not fine:
            return self.send_message("You have no outstanding fines to pay.", sender)

        original_balance = fine.fine_balance

        if amount >= original_balance:
            payment    = original_balance
            fine.fine_balance = Decimal('0.00')
            fine.status       = 'cleared'
            msg = (
                f"Fine '{fine.fine_type.name}' (ID {fine.id}) fully cleared. "
                f"You paid {payment:.2f}."
            )
        else:
            payment    = amount
            fine.fine_balance = original_balance - payment
            msg = (
                f"Applied {payment:.2f} to fine '{fine.fine_type.name}' (ID {fine.id}). "
                f"Remaining balance: {fine.fine_balance:.2f}."
            )

        fine.last_updated = timezone.now()
        fine.save()

        BotFine.objects.create(
            member              = member,
            amount_paid         = payment,
            submitted_chama     = chama_name,
            retrieved_chama     = chama,
            edited_fine       = fine,
            chama               = chama,
            sender = sender
        )

        return self.send_message(msg, sender)
    
    @staticmethod
    def send_message(text, to):
        print(to)
        to_digits = "".join(filter(str.isdigit, to))

        url = f"{FineService.INFOBIP_BASE_URL}/whatsapp/1/message/text"
        headers = {
            "Authorization": f"App {FineService.INFOBIP_API_KEY}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

        payload = {
            "from": FineService.INFOBIP_SENDER_ID,
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
    


