from chamas.models import *
from .models import *
import requests  
from django.conf import settings
from django.http import JsonResponse
import json
from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from authentication.models import Profile


class ServiceGroup:
    INFOBIP_API_KEY   = settings.INFOBIP_API_KEY
    INFOBIP_SENDER_ID = settings.INFOBIP_SENDER_ID     
    INFOBIP_BASE_URL  = "https://api.infobip.com"

    def process_contribution(self, message, sender):
        member_id         = message['member_id']
        raw_amount        = message['amount']
        contribution_name = message['contribution_name']
        chama_name        = message['chama_name']

        # 1) Parse amount into Decimal
        try:
            # support commas: "2,000" → "2000"
            amount = Decimal(str(raw_amount).replace(',', '').strip())
        except (InvalidOperation, AttributeError):
            return self.send_message(
                f"Invalid amount '{raw_amount}'. Please provide a numeric value.",
                sender
            )

        # 2) Find the chama
        chamas = Chama.objects.filter(name__icontains=chama_name)
        if not chamas.exists():
            return self.send_message(f"No chama found matching '{chama_name}'", sender)
        if chamas.count() > 1:
            chamas = chamas.filter(chamamember__member_id=member_id).distinct()
            if not chamas.exists():
                return self.send_message(
                    f"Multiple chamas match '{chama_name}', but none have member {member_id}",
                    sender
                )
        chama = chamas.first()

        # 3) Find the contribution definition
        contributions = Contribution.objects.filter(
            name__icontains=contribution_name,
            chama=chama
        )
        if not contributions.exists():
            return self.send_message(
                f"No contribution named '{contribution_name}' in chama '{chama.name}'",
                sender
            )
        contribution = contributions.first()

        # 4) Find the member
        member = ChamaMember.objects.filter(member_id=member_id, group=chama).first()
        if not member:
            admin_role = Role.objects.filter(name='admin').first()
            admin = ChamaMember.objects.filter(group=chama,role=admin_role).first()

            if admin.user.username != member_id:
                return self.send_message("Member not found in the chama", sender)
            
            else:
                member = admin

            

        # 5) Compute balance
        balance = contribution.amount - amount

        # 6) Create BotContribution record
        bot_contribution = BotContribution.objects.create(
            submitted_contribution = contribution_name,
            retrieved_contribution = contribution,
            amount_paid            = amount,
            submitted_member       = member,
            submitted_chama        = chama_name,
            retrieved_chama        = chama,
            chama                  = chama,
            member_id              = member_id
        )

        # 7) Create real ContributionRecord
        ContributionRecord.objects.create(
            contribution    = contribution,
            date_created    = bot_contribution.date_created,
            amount_expected = contribution.amount,
            amount_paid     = amount,
            balance         = balance,
            member          = member,
            chama           = chama,
        )

        # 8) Notify user
        return self.send_message("Contribution recorded successfully ✅", sender)

    
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
            chama               = chama
        )

        return self.send_message(msg, sender)

    
    def process_loan(self, message, sender):
        from decimal import Decimal
        from django.utils import timezone

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
            chama               = chama
        )

        return self.send_message(msg, sender)
    
    def process_member(self,message,sender):
        name = message['name']
        email = message['email']
        id_number = message['id_number']
        phone = message['phone']
        role = message['role']
        chama_name = message['chama']

        chamas = Chama.objects.filter(name__icontains=chama_name)
        if not chamas.exists():
            return self.send_message(f"No chama found matching '{chama_name}'",sender)
        
        if chamas.count() > 1:
            return self.send_message(f"Multiple chamas match the submitted name,please add the user manually",sender)
        
        chama = chamas.first()

        role = Role.objects.filter(name = str(role)).first()

        if not role:
            return self.send_message("Submitted role is not valid,please submit a valid role",sender)
        
        user = User.objects.filter(username=id_number).first()

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
                chama=chama
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