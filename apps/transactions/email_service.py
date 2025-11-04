from email.mime.image import MIMEImage
import os
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from backend import settings
import logging
from datetime import datetime
import traceback
import sys
from django.utils import formats

logger = logging.getLogger(__name__)

class EmailTemplates:
    """Constantes para los nombres de plantillas disponibles"""
    TRANSACTION = "emails/transaction_notification"  # Cambiado de "transaction_notification"
    WELCOME = "emails/welcome"
    COMPLETED = "emails/transaction_completed" 
    

class EmailService:
    """
    Servicio para el envío de correos electrónicos usando plantillas HTML.
    Permite envío individual y masivo con seguimiento de resultados.
    """
    
    @staticmethod
    def send_email(to_email, subject, template_name, context, from_email=None, attachments=None):
        """
        Envía un correo electrónico usando una plantilla HTML.
        
        Args:
            to_email: Correo o lista de correos destinatarios
            subject: Asunto del correo
            template_name: Nombre de la plantilla a usar (sin extensión)
            context: Diccionario con variables para la plantilla
            from_email: Correo remitente (opcional)
            attachments: Lista de adjuntos (opcional)
            
        Returns:
            dict: Resultado de la operación con éxito/error
        """
        print(f"\n\n====== INICIANDO ENVÍO DE CORREO A {to_email} ======")
        print(f"Plantilla: {template_name}.html")
        print(f"Asunto: {subject}")
        
        try:
            # Completar contexto con variables comunes
            full_context = {
                'current_year': datetime.now().year,
                **context
            }
            
            # Usar el remitente por defecto si no se especifica uno
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            print(f"Remitente: {from_email}")
            # Conexión a Resend
            connection = get_connection(
                host=settings.RESEND_SMTP_HOST,
                port=settings.RESEND_SMTP_PORT,
                username=settings.RESEND_SMTP_USERNAME,
                password=settings.RESEND_API_KEY,
                use_tls=True
            )    
            # Renderizar plantilla HTML
            try:
                print(f"Intentando renderizar plantilla HTML: {template_name}.html")
                html_content = render_to_string(f'{template_name}.html', full_context)
                print(f"HTML renderizado correctamente ({len(html_content)} caracteres)")
            except Exception as template_error:
                print(f"ERROR AL RENDERIZAR PLANTILLA: {str(template_error)}")
                # Mostrar las plantillas disponibles
                from django.template.loader import get_template
                from django.template import TemplateDoesNotExist
                try:
                    get_template(f'{template_name}.html')
                except TemplateDoesNotExist:
                    print(f"LA PLANTILLA {template_name}.html NO EXISTE")
                    print(f"Rutas de plantillas:")
                    for template_dir in settings.TEMPLATES[0]['DIRS']:
                        print(f"- {template_dir}")
                raise
            
            # Extraer el texto plano del HTML
            text_content = strip_tags(html_content)
            print(f"Versión texto generada ({len(text_content)} caracteres)")
                
            # Crear el objeto de correo
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[to_email] if isinstance(to_email, str) else to_email
            )
            print(f"Objeto EmailMultiAlternatives creado")
            
            # Añadir la versión HTML
            email.attach_alternative(html_content, "text/html")
            print(f"Versión HTML adjuntada al correo")  
            # Añadir archivos adjuntos si existen
            if attachments:
                for i, attachment in enumerate(attachments):
                    email.attach(*attachment)
                    print(f"Adjunto {i+1} aadido al correo")
            
            # Enviar el correo
            print(f"INTENTANDO ENVIAR CORREO...")
            email.send(fail_silently=False)
            
            print(f"✓ CORREO ENVIADO EXITOSAMENTE A {to_email}")
            return {"success": True, "message": "Correo enviado correctamente"}
            
        except Exception as e:
            error_msg = f"ERROR AL ENVIAR CORREO: {str(e)}"
            print(error_msg)
            print(f"Tipo de error: {type(e).__name__}")
            
            # Mostrar el stack trace completo
            print("Stack trace:")
            traceback.print_exc()
            
            return {"success": False, "message": error_msg, "error": str(e), "error_type": type(e).__name__}
    
    @staticmethod
    def send_transaction_notification(user_email, user_name, transaction_data):
        """
        Envía una notificación de transacción usando la plantilla específica.
        
        Args:
            user_email: Correo del usuario
            user_name: Nombre del usuario
            transaction_data: Datos de la transacción (dict)
        """
        print(f"\n===== ENVIANDO NOTIFICACIÓN DE TRANSACCIÓN =====")
        print(f"Usuario: {user_name} ({user_email})")
        print(f"Datos de transacción: {transaction_data}")
        formatted_date = formats.date_format(transaction_data.get('date'), "d/m/Y")

        
        context = {
            'user_name': user_name,
            'transaction_id': transaction_data.get('transaction_id'),
            'transaction_date': formatted_date,
            'amount': transaction_data.get('amount'),
            'currency': transaction_data.get('currency', 'USD'),
            'status': transaction_data.get('status', 'Completada'),
            'payment_method': transaction_data.get('payment_method'),
            'description': transaction_data.get('description'),
            'source_currency': transaction_data.get('source_currency'),
            'source_symbol': transaction_data.get('source_currency_symbol'),
            'source_amount': transaction_data.get('source_currency_amount'),
            'destination_currency': transaction_data.get('destination_currency'),
            'exchange_rate': transaction_data.get('exchange_rate'),           
            'destination_symbol': transaction_data.get('destination_currency_symbol'),
            'destination_amount': transaction_data.get('destination_currency_amount'),            
            'dashboard_url': transaction_data.get('dashboard_url', settings.FRONTEND_URL + 'login')
        }
        
        print(f"Contexto preparado para notificación")
        
        return EmailService.send_email(
            to_email=user_email,
            subject=f"Transacción {transaction_data.get('status', 'Procesada')}",
            template_name=EmailTemplates.TRANSACTION,
            context=context
        )

    def send_transaction_completed(user_email, user_name, transaction_data):
        """
        Envía una notificación de transacción usando la plantilla específica.
        
        Args:
            user_email: Correo del usuario
            user_name: Nombre del usuario
            transaction_data: Datos de la transacción (dict)
        """
        print(f"\n===== ENVIANDO NOTIFICACIÓN DE TRANSACCIÓN =====")
        print(f"Usuario: {user_name} ({user_email})")
        print(f"Datos de transacción: {transaction_data}")
        formatted_date = formats.date_format(transaction_data.get('date'), "d/m/Y")

        context = {
            'user_name': user_name,
            'transaction_id': transaction_data.get('transaction_id'),
            'transaction_date': formatted_date,
            'status': transaction_data.get('status', 'Completada'),
            'payment_method': transaction_data.get('payment_method'),
            'description': transaction_data.get('description'),
            'source_currency': transaction_data.get('source_currency'),
            'source_symbol': transaction_data.get('source_currency_symbol'),
            'source_amount': transaction_data.get('source_currency_amount'),
            'destination_currency': transaction_data.get('destination_currency'),
            'destination_symbol': transaction_data.get('destination_currency_symbol'),
            'destination_amount': transaction_data.get('destination_currency_amount'), 
            'exchange_rate': transaction_data.get('exchange_rate'),           
            'dashboard_url': transaction_data.get('dashboard_url', settings.FRONTEND_URL + 'login')
        }
        
        print(f"Contexto preparado para notificación")
        
        return EmailService.send_email(
            to_email=user_email,
            subject=f"Transacción {transaction_data.get('status', 'Procesada')}",
            template_name=EmailTemplates.COMPLETED,
            context=context
        )

    @staticmethod
    def send_welcome_email(user_email, user_name, additional_data=None):
        """
        Envía un correo de bienvenida al registrarse.
        
        Args:
            user_email: Correo del usuario
            user_name: Nombre del usuario
            additional_data: Datos adicionales (opcional)
        """
        print(f"\n===== ENVIANDO EMAIL DE BIENVENIDA =====")
        print(f"Usuario: {user_name} ({user_email})")
        
        additional_data = additional_data or {}
        print(f"Datos adicionales: {additional_data}")
        
        context = {
            'user_name': user_name,
            'email': user_email,
            'app_name': additional_data.get('app_name', 'BrasPer Transferencias'),
            'login_url': additional_data.get('login_url', settings.FRONTEND_URL + '/login'),
            'profile_image_url': additional_data.get('profile_image_url')
        }
        
        print(f"Contexto preparado para email de bienvenida")
        
        return EmailService.send_email(
            to_email=user_email,
            subject=f"Bienvenido a {context['app_name']}",
            template_name=EmailTemplates.WELCOME,
            context=context
        )