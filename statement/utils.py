from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from django.http import HttpResponse
# from decimal import Decimal
import logging

logger = logging.getLogger(__name__)



def send_statement_email(user_email, subject, html_content, pdf_bytes):
    
    try:
        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=to_email
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(f"{user_email}_statement.pdf", pdf_bytes, "application/pdf")

        email.send()
        logger.info(f"Statement email sent to {user_email}")
    except Exception as e:
        logger.error(f"Failed to send statement email to {user_email}: {str(e)}")
        return "Email sending failed"
    return None