from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_whatsapp_message(to_number, message, fallback_sms=False):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    from_whatsapp = settings.TWILIO_WHATSAPP_FROM
    sms_number = to_number.replace('whatsapp:', '')

    try:
        client.messages.create(
            from_=from_whatsapp,
            body=message,
            to=to_number
        )
        print(f"✅ WhatsApp sent to {to_number}")
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        if fallback_sms:
            try:
                client.messages.create(
                    from_=settings.TWILIO_SMS_FROM,
                    body=message,
                    to=sms_number
                )
                print(f"✅ SMS fallback sent to {sms_number}")
            except Exception as sms_e:
                print(f"❌ SMS fallback failed: {sms_e}")

def send_html_email(subject, html_content, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=strip_tags(html_content),
            from_email=None,
            recipient_list=recipient_list,
            fail_silently=True,
            html_message=html_content
        )
        print(f"✅ Email sent to {recipient_list}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
