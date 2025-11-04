from django.core.mail import send_mail
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

try:
    send_mail(
        'Asunto de prueba',
        'Cuerpo del mensaje de prueba',
        'notifications@braspertransferencias.com',
        ['yonelacv30@gmail.com'],
        fail_silently=False,
    )
    print("Correo enviado exitosamente")
except Exception as e:
    print(f"Error al enviar: {str(e)}")