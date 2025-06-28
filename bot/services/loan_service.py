from bot.models import *
from django.conf import settings
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.http import JsonResponse
import requests

class LoanService:
    INFOBIP_API_KEY   = settings.INFOBIP_API_KEY
    INFOBIP_SENDER_ID = settings.INFOBIP_SENDER_ID     
    INFOBIP_BASE_URL  = "https://api.infobip.com"

    def process_loan(self, message, sender):
        from decimal import Decimal
        from django.utils import timezone

        member_id  = message['member_id']
        amount     = Decimal(message['amount'])
        chama_name = message['chama_name']

        terms = chama_name.strip().split()
        q = Q()
        for term in terms:
            q &= Q(name__icontains=term)
        chamas = Chama.objects.filter(q)
        if not chamas.exists():
            return self.send_message(f'No chama found matching "{chama_name}"', sender)
        if chamas.count() > 1:
            chamas = chamas.filter(chamamember__member_id=member_id).distinct()
            if not chamas.exists():
                return self.send_message(
                    f"Multiple chamas match '{chama_name}' but none have member ID '{member_id}'",
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

        loan = (
            LoanItem.objects
            .filter(member=member, chama=chama, balance__gt=0)
            .order_by('applied_on')
            .first()
        )
        if not loan:
            return self.send_message(
                f"You have no outstanding loans in chama '{chama.name}'.",
                sender
            )

        original_balance = loan.balance or Decimal('0.00')
        if amount >= original_balance:
            payment      = original_balance
            loan.balance = Decimal('0.00')
            loan.status  = 'cleared'
            msg = (
                f"Loan (ID {loan.id}, type '{loan.type.name}') fully paid off. You paid {payment:.2f}."
            )
        else:
            payment      = amount
            loan.balance = original_balance - payment
            msg = (
                f"Applied {payment:.2f} to loan (ID {loan.id}, type '{loan.type.name}'). "
                f"Remaining balance: {loan.balance:.2f}."
            )

        loan.total_paid   = (loan.total_paid or Decimal('0.00')) + payment
        loan.last_updated = timezone.now()
        loan.save()

        BotLoan.objects.create(
            member              = member,
            amount_paid         = payment,
            submitted_chama     = chama_name,
            retrieved_chama     = chama,
            updated_loan       = loan,
            chama               = chama,
            sender=sender
        )

        return self.send_message(msg, sender)
    
    @staticmethod
    def send_message(text, to):
        print(to)
        to_digits = "".join(filter(str.isdigit, to))

        url = f"{LoanService.INFOBIP_BASE_URL}/whatsapp/1/message/text"
        headers = {
            "Authorization": f"App {LoanService.INFOBIP_API_KEY}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

        payload = {
            "from": LoanService.INFOBIP_SENDER_ID,
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

    