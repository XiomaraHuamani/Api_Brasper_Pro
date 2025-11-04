import time
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .google_client import GoogleOAuthClient
from .serializers import GoogleAuthSerializer, GoogleUserInfoSerializer
from ..models import User, Role  # Import Role model
from rest_framework.permissions import AllowAny
class GoogleOAuthView(APIView):
    permission_classes = [AllowAny]
    """
    Handle Google OAuth authentication flow with frontend
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = GoogleOAuthClient()

    def post(self, request, *args, **kwargs):
        """
        Handle the OAuth authentication with support for:
        1. Modern frontend flow (Google Sign-In SDK) using ID token
        2. Traditional authorization code flow
        """
        start_time = time.time()
        print('request.data', request.data)
        # Handle both modern and traditional flows
        auth_code = request.data.get('code')
        
        id_token = request.data.get('id_token')  # From Google Sign-In SDK
        
        if not auth_code and not id_token:
            return Response(
                {'error': 'Either authorization code or ID token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_data = None
            error = None

            # Handle modern frontend flow (Google Sign-In SDK)
            if id_token:
                print("Using modern frontend flow with Google Sign-In SDK")
                user_data, error = self.client.verify_oauth_token(id_token)
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

            # Handle traditional authorization code flow
            elif auth_code:
                print("Using traditional authorization code flow")
                token_data, error = self.client.get_token_from_code(auth_code)
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
                access_token = token_data['access_token']
                user_data, error = self.client.get_user_info(access_token)
                if error:
                    return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

            if not user_data or 'email' not in user_data:
                return Response(
                    {'error': 'Failed to get user information'},
                    status=status.HTTP_400_BAD_REQUEST
                )            # Get client role first
            try:
                client_role = Role.objects.get(name=Role.CLIENT)  # Get client role by name constant
                # Get or create user with role
                user, created = User.objects.get_or_create(
                    email=user_data['email'],
                    defaults={
                        'first_name': user_data.get('given_name', ''),
                        'last_name': user_data.get('family_name', ''),
                        'is_active': True,
                        'role': client_role  # Assign role during creation
                    }
                )
                user = User.objects.get(email=user.email)

                if created:
                    print("✓ User created with client role")
                else:
                    print("✓ Existing user found")
            except Role.DoesNotExist:
                print("❌ Client role not found in database")
                return Response(
                    {'error': 'System configuration error: Client role not found'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            user = User.objects.get(email=user)
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            tokens = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }

            end_time = time.time()
            print(f"Total OAuth flow took {end_time - start_time:.3f} seconds")            # Prepare response with role information
            role_str = str(user.role.name) if (hasattr(user, 'role') and user.role) else 'client'
            print("user info", user.first_name, user.last_name, user.email)
            return Response({
                'tokens': tokens,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'role': role_str
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
