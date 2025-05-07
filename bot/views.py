import os, json, re
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .services import ServiceGroup

INFOBIP_API_KEY    = settings.INFOBIP_API_KEY
INFOBIP_SENDER_ID  = settings.INFOBIP_SENDER_ID  # e.g. "447500000000"
INFOBIP_BASE_URL   = "https://api.infobip.com"

def send_infobip_whatsapp(to, text):
    url = f"{INFOBIP_BASE_URL}/whatsapp/1/message/text"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "from": INFOBIP_SENDER_ID,
        "to": to,
        "content": { "text": text }
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.ok

# @csrf_exempt
# def infobip_webhook(request):
#     if request.method != "POST":
#         return JsonResponse({"error":"invalid method"}, status=405)

#     data = json.loads(request.body)
#     # 1) Save raw payload for debugging
#     RawWhatsAppMessage.objects.create(payload=data)

#     # 2) Extract messages
#     for msg in data.get("messages", []):
#         sender = msg.get("from")
#         text   = msg.get("text", {}).get("body", "").strip()
        
#         # Basic format-check
#         tag_match = re.search(r"#(Contribution|Loan|Fine)", text, re.IGNORECASE)
#         amount_match = re.search(r"Ksh\s*([\d,]+(?:\.\d{1,2})?)", text)
#         name_match = re.search(r"–\s*(\w+)", text) 
        
#         if not tag_match or not amount_match or not name_match:
#             # malformed → ask for clarification
#             reply = (
#                 "Sorry, I couldn't understand your message. "
#                 "Please send like: “Confirmed. Ksh1,000 sent to John. #Contribution – Alice”"
#             )
#             send_infobip_whatsapp(sender, reply)
#             continue

#         tag    = tag_match.group(1).lower()
#         amount = amount_match.group(1).replace(",", "")
#         name   = name_match.group(1)

#         # Try to match to a User
#         user = None
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
#         try:
#             user = User.objects.get(profile__phone_number=sender)
#         except User.DoesNotExist:
#             # leave as None; admin can resolve later
#             pass

#         # 3) Save transaction
#         BotTransaction.objects.create(
#             user=user,
#             phone_number=sender,
#             message_text=text,
#             transaction_type=tag,
#             amount=amount,
#         )
#         send_infobip_whatsapp(sender, "✅ Your transaction has been recorded. Thank you!")
    
#     return JsonResponse({"status":"received"})

@csrf_exempt
def receive_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=405)

    data = json.loads(request.body)

    for result in data.get("results", []):
        sender = result.get("from")
        text = result.get("message", {}).get("text", "").strip()

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
            required_fields = ["member ID","amount","chama name"]
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
                "member_id": lines[1],
                "amount" : lines[2],
                "chama_name": lines[3]
            }

            return svc.process_fine(payload,sender)
        
        elif tag == "#LOAN":
            required_fields = ["member_id","amount","chama name"]
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
                "member_id": lines[1],
                "amount": lines[2],
                "chama_name": lines[3]
            }

            return svc.process_loan(payload,sender)


    return JsonResponse({"status": "no inbound messages"}, status=200)