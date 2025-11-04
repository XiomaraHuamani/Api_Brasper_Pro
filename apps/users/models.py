from datetime import timedelta
from django.utils.timezone import now
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator

AUTH_PROVIDERS = {"email": "email", "google": "google"}


class Role(models.Model):
    STAFF = "staff"
    CLIENT = "client"
    SALES = "sales"

    ROLE_CHOICES = [
        (STAFF, _("Staff")),
        (CLIENT, _("Client")),
        (SALES, _("sales")),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=CLIENT,
        unique=True,
        verbose_name=_("Role Name"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):

    COUNTRY_PHONE_CODE_CHOICES = [
        ("+1", "Estados Unidos"),
        ("+1", "Canadá"),
        ("+52", "México"),
        ("+55", "Brasil"),
        ("+54", "Argentina"),
        ("+57", "Colombia"),
        ("+56", "Chile"),
        ("+58", "Venezuela"),
        ("+51", "Perú"),
        ("+593", "Ecuador"),
        ("+53", "Cuba"),
        ("+591", "Bolivia"),
        ("+506", "Costa Rica"),
        ("+507", "Panamá"),
        ("+598", "Uruguay"),
        ("+34", "España"),
        ("+49", "Alemania"),
        ("+33", "Francia"),
        ("+39", "Italia"),
        ("+44", "Reino Unido"),
        ("+7", "Rusia"),
        ("+380", "Ucrania"),
        ("+48", "Polonia"),
        ("+40", "Rumania"),
        ("+31", "Países Bajos"),
        ("+32", "Bélgica"),
        ("+30", "Grecia"),
        ("+351", "Portugal"),
        ("+46", "Suecia"),
        ("+47", "Noruega"),
        ("+86", "China"),
        ("+91", "India"),
        ("+81", "Japón"),
        ("+82", "Corea del Sur"),
        ("+62", "Indonesia"),
        ("+90", "Turquía"),
        ("+63", "Filipinas"),
        ("+66", "Tailandia"),
        ("+84", "Vietnam"),
        ("+972", "Israel"),
        ("+60", "Malasia"),
        ("+65", "Singapur"),
        ("+92", "Pakistán"),
        ("+880", "Bangladés"),
        ("+966", "Arabia Saudita"),
        ("+20", "Egipto"),
        ("+27", "Sudáfrica"),
        ("+234", "Nigeria"),
        ("+254", "Kenia"),
        ("+212", "Marruecos"),
        ("+213", "Argelia"),
        ("+256", "Uganda"),
        ("+233", "Ghana"),
        ("+237", "Camerún"),
        ("+225", "Costa de Marfil"),
        ("+221", "Senegal"),
        ("+255", "Tanzania"),
        ("+249", "Sudán"),
        ("+218", "Libia"),
        ("+216", "Túnez"),
        ("+61", "Australia"),
        ("+64", "Nueva Zelanda"),
        ("+679", "Fiji"),
        ("+675", "Papúa Nueva Guinea"),
        ("+676", "Tonga"),
        ("+98", "Irán"),
        ("+964", "Iraq"),
        ("+962", "Jordania"),
        ("+961", "Líbano"),
        ("+965", "Kuwait"),
        ("+971", "Emiratos Árabes Unidos"),
        ("+968", "Omán"),
        ("+974", "Catar"),
        ("+973", "Bahrein"),
        ("+967", "Yemen"),
        ("+1", "República Dominicana"), 
    ]

    DOCUMENT_TYPE_CHOICES = [
        ("DNI", "DNI - Documento Nacional de Identidad"),
        ("CE", "CE - Carnet de Extranjería"),
        ("RG", "RG - Registro Geral"),
        ("CRNM", "CRNM - Carteira de Registro Nacional Migratório"),
        ("RNE", "RNE - Registro Nacional de Extranjero"),
        ("PAS", "PAS - Número de Pasaporte"),
        ("OTROS", "Otros"),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ("soltero", "Soltero/a"),
        ("casado", "Casado/a"),
        ("divorciado", "Divorciado/a"),
    ]


    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="El número de teléfono debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos.",
    )

    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )

    type_identity_document = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        blank=True,
        null=True,
    )

    document_number = models.CharField(
        max_length=20,
        verbose_name=_("Document Number"),
        null=True,
        blank=True,
    )

    country_code = models.CharField(max_length=50, choices=COUNTRY_PHONE_CODE_CHOICES)

    marital_status = models.CharField(
        max_length=50,
        choices=MARITAL_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Estado Civil")
    )

    occupation = models.CharField(max_length=50, null=True, blank=True)

    work_situation = models.CharField(max_length=50, null=True, blank=True)
    
    country = models.CharField(
        max_length=100, verbose_name=_("Country"), null=True, blank=True
    )

    city = models.CharField(max_length=50, null=True, blank=True)

    province = models.CharField(max_length=50, null=True, blank=True)

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        # unique=True,
        verbose_name=_("Phone Number"),
        help_text=_("Contact phone number with country code"),
        null=True,  # Temporalmente permitimos null
        blank=True,  # Temporalmente permitimos blank
    )

    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get("email")
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name=_("role"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "country_code", "phone_number", "password"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def is_client(self):
        """Check if user is a client"""
        return self.role and self.role.name == Role.CLIENT

    @property
    def is_staff_member(self):
        """Check if user is a staff member"""
        return self.role and self.role.name == Role.STAFF

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def set_role(self, role_name):
        """Set user role to either staff or client"""
        if role_name not in [Role.STAFF, Role.CLIENT]:
            raise ValueError("Invalid role name. Must be either 'staff' or 'client'")
        role, _ = Role.objects.get_or_create(name=role_name)
        self.role = role
        self.save()


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.first_name} - otp code"
    
    def is_expired(self):
        return now() > self.created_at + timedelta(minutes=15) 
