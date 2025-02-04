import string
from django.forms import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import User
import datetime
import random
import re



def generate_otp(*,k=4):
    return ''.join(random.choices(string.digits, k=k))


def jwt_auth(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return {
        'refresh': str(refresh),
        'access': str(access),
    }

def send_email(user_email, subject, template):
    subject = subject
    from_email = settings.EMAIL_HOST_USER
    to_email = [user_email]

    email = EmailMultiAlternatives(
        subject=subject,
        body=template,
        from_email=from_email,
        to=to_email
    )

    email.content_subtype = 'email'
    email.attach_alternative(template, "text/html")

    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Failed to send email t{user_email}: {str(e)}")
        return "Email sending failed"
    return None

def validate_otp(user_email, otp, ttl_minutes=5):
    try:
        user = User.objects.get(email=user_email).first()
    except User.DoesNotExist:
        return False
    if not user.otp or not user.otp_created_at or datetime.timezone.now() > datetime.timedelta(minutes=ttl_minutes):
        user.reset_otp()
        return "The otp has expired. Please request a new one"
    
    if user.otp == otp:
        user.reset_otp()
        return "Otp validation successful"
    return "Invalid otp"


def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be atleast 8 characters long")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must contain atleast one uppercase letter")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Password must contain atleast one lowercase letter")
    if not re.search(r'[0-9]', value):
        raise ValidationError("Password must contain atleast one number")
    if not re.search(r'[@_!#$%^&*()<>?/\|}{~:]', value):
        raise ValidationError("Password must contain atleast one special character")
    return value



def normalize_number(number):
    if number.startswith("+234"):
        return '' + number[4:]
    elif number.startswith("+"):
        raise ValueError("Only Nigerian phone numbers starting with +234 are allowed")
    elif number.startswith("234"):
        return number
    elif len(number) != 11:
        raise ValueError("Phone number must be 11 digits")
    return number