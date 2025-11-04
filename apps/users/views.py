from email.mime.image import MIMEImage
from django.shortcuts import get_object_or_404
from apps.users.permissions import IsStaff
from apps.users.utils import generate_login_response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.core.mail import EmailMultiAlternatives, get_connection
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    RoleSerializer,
    StaffRegisterSerializer,
    UserPersonalDataSerializer,
    UserSerializer,
    UserFormSerializer,
    PasswordResetRequestSerializer,
)
from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from .models import OneTimePassword, User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings

import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from google.oauth2 import id_token
from google.auth.transport import requests
# users/views.py
from .models import Role  # Asegúrate de que la ruta de importación sea correcta

User = get_user_model()


# Manage Users
class StaffRegisterView(GenericAPIView):
    serializer_class = StaffRegisterSerializer
    permission_classes = [IsStaff]
    

    def get_queryset(self):
        """
        Retorna solo usuarios con rol de staff
        """
        return User.objects.filter(role__name="staff")

    def get(self, request, pk=None):
        if pk:
            try:
                # Obtener un usuario staff específico
                user = self.get_queryset().get(pk=pk)
                serializer = self.serializer_class(user)
                return Response(
                    {"status": "success", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Staff user not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            # Obtener todos los usuarios staff
            users = self.get_queryset()
            serializer = self.serializer_class(users, many=True)
            return Response(
                {"status": "success", "total": users.count(), "data": serializer.data},
                status=status.HTTP_200_OK,
            )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"user": serializer.data, "message": "Staff registrado exitosamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response(
                {"error": "ID de usuario requerido para actualización"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            user, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            if "email" in request.data:
                user.username = request.data["email"]
            serializer.save()
            return Response(
                {
                    "user": serializer.data,
                    "message": "Usuario actualizado exitosamente",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response(
                {"error": "ID de usuario requerido para eliminación"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(
                {"message": "Usuario eliminado exitosamente"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "message": "Client creado exitosamente",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response(
                {"error": "ID de usuario requerido para actualización"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Agregar prints para debug
        print("Request data:", request.data)
        print("User before update:", user.__dict__)

        serializer = self.serializer_class(
            user, 
            data=request.data, 
            partial=True, 
            context={"request": request}
        )

        print("Serializer valid:", serializer.is_valid())
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)

        if serializer.is_valid():
            if "email" in request.data:
                user.username = request.data["email"]
            serializer.save()
            print("User after update:", user.__dict__)
            return Response(
                {
                    "user": serializer.data,
                    "message": "Usuario actualizado exitosamente",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Lista y creación de usuarios
class UserListCreateView(ListCreateAPIView):
   queryset = User.objects.all()
   serializer_class = UserSerializer

   def get(self, request, role=None, *args, **kwargs):
       if role and role in ['sales', 'staff', 'client']:
           queryset = self.get_queryset().filter(role__name=role)
       else:
           queryset = self.get_queryset()
       
       serializer = self.get_serializer(queryset, many=True)
       return Response(serializer.data)

# Detalle, actualización y eliminación de un usuario específico
class UserRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["PATCH"])  
def update_user_personal_data(request, user_id):
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserPersonalDataSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that extends from TokenRefreshView
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = user.tokens()

            # Obtenemos solo el nombre del rol
            role_name = user.role.name if user.role else None
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": tokens,
                    "role": role_name,  # Solo devolvemos el nombre del rol
                    "message": "Inicio de sesión exitoso",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            return Response(
                {"message": "Sesión cerrada exitosamente"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Error al cerrar sesión", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client
class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
   def complete_login(self, request, app, token, **kwargs):
       try:
           id_token_object = id_token.verify_oauth2_token(
               token.token,
               requests.Request(),
               app.client_id,
               clock_skew_in_seconds=5
           )

           return self.get_provider().sociallogin_from_response(request, {
               'id': id_token_object['sub'],
               'email': id_token_object['email'],
               'name': id_token_object.get('name', ''),
               'given_name': id_token_object.get('given_name', ''),
               'family_name': id_token_object.get('family_name', ''),
               'picture': id_token_object.get('picture', '')
           })
       except Exception as e:
           print(f"Error verifying token: {e}")
           raise OAuth2Error(str(e))

class GoogleLoginWithToken(SocialLoginView):
   adapter_class = CustomGoogleOAuth2Adapter
   callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL 

   def post(self, request, *args, **kwargs):
       token = request.data.get('access_token')
       if token:
           request.data['access_token'] = token

       response = super().post(request, *args, **kwargs)
       user = self.request.user

       if user:
           try:
               # Verificar si el rol es None
               if not hasattr(user, 'role') or user.role is None:
                   client_role = Role.objects.get(id=2)
                   user.role = client_role
                   user.save()
                   print(f"Rol asignado: {user.role}")
               refresh = RefreshToken.for_user(user)
               # Solo acceder a role.name si role no es None
               role_str = str(user.role.name) if (hasattr(user, 'role') and user.role) else 'client'
               response.data.update({
                   "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                   },
                   "role": role_str,
                   "user": {
                       "id": user.id,
                       "email": user.email,
                       "name": f"{user.first_name} {user.last_name}".strip()
                   }
               })
           except Exception as e:
               print(f"Error: {str(e)}")
               response.data.update({"role": "client"}) 

       return response
class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        print("\n=== Inicio GoogleLoginCallback GET ===")
        code = request.GET.get("code")
        print("Código recibido:", code[:20] if code else None)

        if code is None:
            print("No se recibió código")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_endpoint_url = "http://localhost:8000/api/v1/auth/google/"
        print(f"Haciendo POST a: {token_endpoint_url}")
        response = requests.post(token_endpoint_url, data={"code": code})
        print("Respuesta del endpoint:", response.status_code)
        print("=== Fin GoogleLoginCallback GET ===\n")
        return Response(response.json(), status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        print("\n=== Inicio GoogleLoginCallback POST ===")
        
        # 1. Obtener código de acceso
        code = request.data.get("access_token")
        print("1. Código de acceso recibido:", code[:20] if code else None)

        if not code:
            print("Error: No se recibió código de acceso")
            return Response(
                {"error": "Authorization code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Intercambiar código por token de Google
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": "http://localhost:8000/api/v1/auth/google/callback/",
            "grant_type": "authorization_code",
        }
        print("2. Solicitando token a Google con datos:", {k: v[:20] if k != "grant_type" else v for k, v in data.items()})
        
        response = requests.post(token_url, data=data)
        print("3. Respuesta de Google:", response.status_code)
        print("Contenido de respuesta:", response.text[:100])

        if response.status_code != 200:
            print("Error al obtener token de Google")
            return Response(
                {"error": "Failed to fetch token from Google"},
                status=response.status_code,
            )

        google_data = response.json()
        print("4. Token de Google obtenido exitosamente")

        # 3. Obtener información del usuario
        google_token = google_data.get("access_token")
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f'Bearer {google_token}'}
        print("5. Solicitando información del usuario a Google")
        
        userinfo_response = requests.get(userinfo_url, headers=headers)
        print("6. Respuesta de información del usuario:", userinfo_response.status_code)
        
        google_user = userinfo_response.json()
        print("7. Datos del usuario obtenidos:", {k: v for k, v in google_user.items() if k != 'email'})  # Excluimos email por privacidad

        # 4. Buscar usuario
        try:
            user = User.objects.get(email=google_user['email'])
            print("8. Usuario encontrado en la base de datos")
        except User.DoesNotExist:
            print("8. Usuario no encontrado")
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 5. Generar respuesta
        jwt_token = "example_jwt_token"
        print("9. JWT token generado")

        response_data = {
            "access": jwt_token,
            "refresh": google_data.get("refresh_token"),
            "google_access": google_data.get("access_token"),
            "role": user.role,
            "user": {
                "id": user.id,
                "email": user.email,
            }
        }
        print("10. Preparando respuesta final")
        print("=== Fin GoogleLoginCallback POST ===\n")
        
        return Response(response_data, status=status.HTTP_200_OK)

class UserProfileView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.filter(id=pk).first()
            
            if not user:
                return Response(
                    {
                        "success": False,
                        "message": f"No se encontró ningún usuario con el ID {pk}"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(user)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def patch(self, request, *args, **kwargs):
        """
        Actualizar perfil del usuario
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Perfil actualizado exitosamente",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class VerifyEmailView(GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, token, *args, **kwargs):
        """
        Verificar email del usuario
        """
        try:
            user = User.objects.get(verification_token=token)
            if not user.is_verified:
                user.is_verified = True
                user.verification_token = None
                user.save()

                return Response(
                    {"success": True, "message": "Email verificado exitosamente"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"success": False, "message": "El email ya está verificado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Token de verificación inválido"},
                status=status.HTTP_404_NOT_FOUND,
            )

class ChangePasswordView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        """
        Cambiar contraseña del usuario
        """
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"success": False, "message": "Contraseña actual incorrecta"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"success": True, "message": "Contraseña actualizada exitosamente"},
            status=status.HTTP_200_OK,
        )


# Manage Roles


class RoleCreateView(GenericAPIView):
    serializer_class = RoleSerializer
    permission_classes = [IsStaff]

    def get_object(self, role_id):
        return get_object_or_404(Role, id=role_id)

    def post(self, request):
        """Create a new role"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"role": serializer.data, "message": "Role created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, role_id=None):
        """Get a single role or list all roles"""
        if role_id:
            role = self.get_object(role_id)
            serializer = self.serializer_class(role)
            return Response(serializer.data, status=status.HTTP_200_OK)

        roles = Role.objects.all()
        serializer = self.serializer_class(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, role_id):
        """Update a role"""
        try:
            # Obtener la instancia existente
            role = self.get_object(role_id)

            # Crear el serializer con la instancia y los nuevos datos
            serializer = self.serializer_class(
                instance=role,
                data=request.data,
                partial=False,  # Requiere todos los campos
            )

            # Validar los datos
            if serializer.is_valid():
                # Guardar los cambios
                serializer.save()

                return Response(
                    {"role": serializer.data, "message": "Role updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": serializer.errors, "message": "Invalid data provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Role.DoesNotExist:
            return Response(
                {
                    "error": "Role not found",
                    "message": "The role you are trying to update does not exist",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "error": str(e),
                    "message": "An error occurred while updating the role",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, role_id):
        """Partially update a role"""
        role = self.get_object(role_id)
        serializer = self.serializer_class(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "role": serializer.data,
                    "message": "Role partially updated successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, role_id):
        """Delete a role"""
        role = self.get_object(role_id)
        role.delete()
        return Response(
            {"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )



class UserListCreateView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         GenericAPIView):
    queryset = User.objects.all().select_related('role')
    serializer_class = UserFormSerializer # Cambia según necesidad

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserRetrieveUpdateDestroyView(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    GenericAPIView):
    queryset = User.objects.all().select_related('role')
    serializer_class = UserFormSerializer


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data['email']
        frontend_url = serializer.validated_data['frontend_url']
        try:
            user = User.objects.get(email=email)
             # Elimina tokens anteriores para ese usuario
            OneTimePassword.objects.filter(user=user).delete()
            # Crea un nuevo token
            reset_token = OneTimePassword.objects.create(user=user)
            token = str(reset_token.otp)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            print(f"Este es el uid: {uid}")
            print(f"Este es el token: {token}")
            print(f"Este es el reset_link: {reset_link}")
            context = {
                "reset_link": reset_link,
                "current_year": now().year,
                "name": user.name if hasattr(user, 'name') and user.name else '',
            }
            subject = "Restablece tu contraseña"
            text_content = f"Restablece tu contraseña en este enlace: {reset_link}"
            html_content = render_to_string("emails/password_reset.html", context)

            connection = get_connection(
                host=settings.RESEND_SMTP_HOST,
                port=settings.RESEND_SMTP_PORT,
                username=settings.RESEND_SMTP_USERNAME,
                password=settings.RESEND_API_KEY,
                use_tls=True
            )

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection
            )
            email_msg.attach_alternative(html_content, "text/html")

            email_msg.send()
        except User.DoesNotExist:
            print("El usuario no existe")
            pass 
        return Response({"message": "Si el correo existe, se ha enviado un enlace"}, status=200)

class PasswordResetValidateView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        uid = request.query_params.get("uid")
        token = request.query_params.get("token")
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            reset_token = OneTimePassword.objects.get(user=user, otp=token)
            if reset_token.is_expired():
                reset_token.delete()
                return Response({"valid": False, "reason": "expired"}, status=400)
            return Response({"valid": True})
        except OneTimePassword.DoesNotExist:
            return Response({"valid": False}, status=400)
        except Exception as e:
            print(f"Error en validación: {e}")
            return Response({"valid": False}, status=400)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            reset_token = OneTimePassword.objects.get(user=user, otp=token)
            if reset_token.is_expired():
                reset_token.delete()
                return Response({"error": "Token expirado"}, status=400)

            user.set_password(new_password)
            user.save()
            # Elimina el token después de usarlo
            reset_token.delete()

            return Response({"message": "Contraseña restablecida con éxito"})

        except OneTimePassword.DoesNotExist:
            return Response({"error": "Token inválido"}, status=400)
        except Exception as e:
            print(f"Error al restablecer la contraseña: {e}")
            return Response({"error": "Token inválido o expirado"}, status=400)