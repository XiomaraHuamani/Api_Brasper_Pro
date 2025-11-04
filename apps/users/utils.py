from django.core.mail import EmailMessage
import random
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from apps.users.serializers import UserSerializer
from .models import User, OneTimePassword
from django.contrib.sites.shortcuts import get_current_site



def send_generated_otp_to_email(email, request): 
    subject = "One time passcode for Email verification"
    otp=random.randint(1000, 9999) 
    current_site=get_current_site(request).domain
    user = User.objects.get(email=email)
    email_body=f"Hi {user.first_name} thanks for signing up on {current_site} please verify your email with the \n one time passcode {otp}"
    from_email=settings.EMAIL_HOST
    otp_obj=OneTimePassword.objects.create(user=user, otp=otp)
    #send the email 
    d_email=EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
    d_email.send()


def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()

def generate_login_response(user, message="Inicio de sesión exitoso"):
    tokens = user.tokens()
    role_name = user.role.name if user.role else None

    return Response(
        {
            "user": UserSerializer(user).data,  # Serializa al usuario
            "tokens": tokens,                   # Tokens de acceso y refresh
            "role": role_name,                  # Rol del usuario
            "message": message,                 # Mensaje de éxito
        },
        status=status.HTTP_200_OK,
    )