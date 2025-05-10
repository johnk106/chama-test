import os, json, re
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .services import ServiceGroup
from chamas.decorators import is_user_chama_member
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from chamas.models import *
from .models import *



INFOBIP_API_KEY    = settings.INFOBIP_API_KEY
INFOBIP_SENDER_ID  = settings.INFOBIP_SENDER_ID  # e.g. "447500000000"
INFOBIP_BASE_URL   = "https://api.infobip.com"



@csrf_exempt
def receive_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=405)

    data = json.loads(request.body)

    for result in data.get("results", []):
        # 1) Grab the real sender key
        sender = result.get("sender")

        # 2) Pull text from the first content element
        content = result.get("content", [])
        text = ""
        if content and isinstance(content, list):
            text = content[0].get("text", "").strip()

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            return ServiceGroup.send_message(
                "Empty message received. Please resend with a valid tag.",
                sender
            )

        tag = lines[0].upper()
        if tag not in ("#CONTRIBUTION", "#FINE", "#LOAN"):
            return ServiceGroup.send_message(
                "Invalid message tag. First line must be one of #CONTRIBUTION, #LOAN, or #FINE.",
                sender
            )

        svc = ServiceGroup()
        if tag == "#CONTRIBUTION":
            required_fields = ["member ID", "amount", "contribution name", "chama name"]
            if len(lines) < 5:
                missing = required_fields[len(lines) - 1]
                return ServiceGroup.send_message(
                    f"Missing required field: {missing}. Please resend in the format:\n"
                    "#CONTRIBUTION\n"
                    "member_id\n"
                    "amount\n"
                    "contribution_name\n"
                    "chama_name",
                    sender
                )

            payload = {
                "member_id":         lines[1],
                "amount":            lines[2],
                "contribution_name": lines[3],
                "chama_name":        lines[4],
            }
            return svc.process_contribution(payload, sender)

        elif tag == "#FINE":
            required_fields = ["member ID", "amount", "chama name"]
            if len(lines) < 4:
                missing = required_fields[len(lines) - 1]
                return ServiceGroup.send_message(
                    f"Missing required field: {missing}. Please resend in the format:\n"
                    "#FINE\n"
                    "member_id\n"
                    "amount\n"
                    "chama_name",
                    sender
                )

            payload = {
                "member_id":  lines[1],
                "amount":     lines[2],
                "chama_name": lines[3],
            }
            return svc.process_fine(payload, sender)

        elif tag == "#LOAN":
            required_fields = ["member ID", "amount", "chama name"]
            if len(lines) < 4:
                missing = required_fields[len(lines) - 1]
                return ServiceGroup.send_message(
                    f"Missing required field: {missing}. Please resend in the format:\n"
                    "#LOAN\n"
                    "member_id\n"
                    "amount\n"
                    "chama_name",
                    sender
                )

            payload = {
                "member_id":  lines[1],
                "amount":     lines[2],
                "chama_name": lines[3],
            }
            return svc.process_loan(payload, sender)

    return JsonResponse({"status": "no inbound messages"}, status=200)

@login_required(login_url='/user/Login')
@is_user_chama_member
def bot_records(request,chama_id):
    chama = Chama.objects.filter(id=chama_id).first()
    contributions = BotContribution.objects.filter(chama=chama).order_by('-id').all()

    loans = BotLoan.objects.filter(chama=chama).order_by('-id').all()

    fines = BotFine.objects.filter(chama=chama).order_by('-id').all()




    return render(request,'bot/records.html',{
        'contributions':contributions,
        'loans':loans,
        'fines':fines
    })