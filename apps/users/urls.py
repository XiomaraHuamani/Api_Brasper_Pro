from django.urls import path
from .views import (
    CustomTokenRefreshView,
    GoogleLoginCallback,
    GoogleLoginWithToken,
    LogoutView,
    RegisterView,
    LoginView,
    RoleCreateView,
    StaffRegisterView,
    UserListCreateView,
    UserProfileView,
    UserRetrieveUpdateDeleteView,
    update_user_personal_data,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    PasswordResetRequestView,
    PasswordResetValidateView,
    PasswordResetConfirmView,
)
from .oauth.views import GoogleOAuthView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("register/<int:pk>/", RegisterView.as_view(), name="register-update"),
    path("staff/register/", StaffRegisterView.as_view(), name="staff-register"),
    path("staff/register/<int:pk>/", StaffRegisterView.as_view(), name="staff-update"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # path('google/', GoogleSocialAuthView.as_view(), name='google-auth'),
    path("profile/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("roles/create/", RoleCreateView.as_view(), name="role-create"),
    # Roles
    path("roles/", RoleCreateView.as_view()),
    path("roles/<int:role_id>/", RoleCreateView.as_view()),
    # users all
    path('users/rol/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/rol/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    
    # Edit personal data of user
    path(
        "user/<int:user_id>/personal-data/",
        update_user_personal_data,
        name="update_user_personal_data",
    ),
    path("google/", GoogleLoginWithToken.as_view(), name="google_login"),
    path(
        "google/callback/",
        GoogleLoginCallback.as_view(),
        name="google_login_callback",
    ),
    path('users/', UserListCreateView.as_view(), name='user-list-create'), 
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('password-reset/validate/', PasswordResetValidateView.as_view()),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view()), # Listar y crear usuarios
    path('users/<int:pk>/', UserRetrieveUpdateDeleteView.as_view(), name='user-detail'),  # Operaciones en un usuario específico
    path('users/<str:role>/', UserListCreateView.as_view()),
    path('auth/google/', GoogleOAuthView.as_view(), name='google_oauth'),
]
