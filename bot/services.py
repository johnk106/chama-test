from chamas.models import *
from .models import *
import requests  
from django.conf import settings
from django.http import JsonResponse
import json

class ServiceGroup:
    INFOBIP_API_KEY   = settings.INFOBIP_API_KEY
    INFOBIP_SENDER_ID = settings.INFOBIP_SENDER_ID     
    INFOBIP_BASE_URL  = "https://api.infobip.com"

    def process_contribution(self, message, sender):
        member_id         = message['member_id']
        amount            = message['amount']
        contribution_name = message['contribution_name']
        chama_name        = message['chama_name']

        
        chamas = Chama.objects.filter(name__icontains=chama_name)
        if not chamas.exists():
            return self.send_message(
                f"No chama found matching name '{chama_name}'",
                sender
            )

        if chamas.count() > 1:
            chamas = chamas.filter(chamamember__member_id=member_id).distinct()
            if not chamas.exists():
                return self.send_message(
                    f"Multiple chamas match '{chama_name}', but none have member {member_id}",
                    sender
                )

        chama = chamas.first()

        
        contributions = Contribution.objects.filter(
            name__icontains=contribution_name,
            chama=chama
        )
        if not contributions.exists():
            return self.send_message(
                f"No contribution named '{contribution_name}' in chama '{chama.name}'",
                sender
            )

        
        BotContribution.objects.create(
            submitted_contribution = contribution_name,
            retrieved_contribution = contributions.first(),
            amount_paid           = amount,
            submitted_member      = member_id,
            submitted_chama       = chama_name,
            retrieved_chama       = chama
        )

        
        return self.send_message(
            "Contribution recorded successfully ✅",
            sender
        )
    
    def process_fine(self, message, sender):
        member_id  = message['member_id']
        amount     = Decimal(message['amount'])
        chama_name = message['chama_name']

        
        chamas = Chama.objects.filter(name__icontains=chama_name)
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
            return self.send_message(
                f"No member with ID '{member_id}' in chama '{chama.name}'",
                sender
            )

        
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
            fine.paid_fine_amount += original_balance
            fine.fine_balance = Decimal('0')
            fine.status = 'cleared'
            msg = (
                f"Fine '{fine.fine_type.name}' (ID {fine.id}) fully cleared. "
                f"You paid {original_balance:.2f}."
            )
        else:
            fine.fine_balance     = original_balance - amount
            fine.paid_fine_amount += amount
            msg = (
                f"Applied {amount:.2f} to fine '{fine.fine_type.name}' (ID {fine.id}). "
                f"Remaining balance: {fine.fine_balance:.2f}."
            )

        fine.last_updated = timezone.now()
        fine.save()

        
        BotFine.objects.create(
            member             = member,
            amount_paid        = amount,
            submitted_chama    = chama_name,
            retrieved_chama    = chama,
            edited_fine        = fine
        )

        return self.send_message(msg, sender)
    
    def process_loan(self, message, sender):
        member_id  = message['member_id']
        amount     = Decimal(message['amount'])
        chama_name = message['chama_name']

        chamas = Chama.objects.filter(name__icontains=chama_name)
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
            return self.send_message(
                f"No member with ID '{member_id}' in chama '{chama.name}'",
                sender
            )

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
            loan.total_paid = (loan.total_paid or Decimal('0.00')) + original_balance
            loan.balance    = Decimal('0.00')
            loan.status     = 'cleared'
            paid_amount     = original_balance
            msg = (
                f"Loan (ID {loan.id}, type '{loan.type.name}') fully paid off. "
                f"You paid {original_balance:.2f}."
            )
        else:
            loan.total_paid = (loan.total_paid or Decimal('0.00')) + amount
            loan.balance   -= amount
            paid_amount     = amount
            msg = (
                f"Applied {amount:.2f} to loan (ID {loan.id}, type '{loan.type.name}'). "
                f"Remaining balance: {loan.balance:.2f}."
            )

        loan.last_updated = timezone.now()
        loan.save()

        new_bot_loan_update = BotLoan.objects.create(
            member=member_id,
            amount_paid=amount,
            submitted_chama=chama_name,
            retrieved_chama=chama,
            updated_loan=loan
        )

        # 5) Send confirmation
        return self.send_message(msg, sender)



    @staticmethod
    def send_message(text, to):
        to_digits = "".join(filter(str.isdigit, to))

        url = f"{ServiceGroup.INFOBIP_BASE_URL}/whatsapp/1/message/text"
        headers = {
            "Authorization": f"App {ServiceGroup.INFOBIP_API_KEY}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

        payload = {
            "from": ServiceGroup.INFOBIP_SENDER_ID,
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