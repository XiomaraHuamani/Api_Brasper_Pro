# Create your models here.
from datetime import datetime
import random
import uuid
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.coin.models import Currency
from apps.users.models import User

class BankAccount(models.Model):
    # Campo para identificar el país de la cuenta
    COUNTRY_CHOICES = [
        ('BR', 'Brasil'),
        ('PE', 'Perú'),
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('personal', 'Cuenta Personal'),
        ('business', 'Cuenta Empresa'),
    ]
    
    # Campos base que comparten ambos países
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    country = models.CharField(
        max_length=2, 
        choices=COUNTRY_CHOICES,
        verbose_name='País'
    )

    # Campos específicos para Perú según el formulario mostrado
    bank_name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Banco'
    )
    
    # Campos del titular según el formulario de Perú
    holder_names = models.CharField(
        max_length=255,
        verbose_name='Nombres',
        null=True,  # Permitimos valores nulos
        blank=True 
    )
    holder_surnames = models.CharField(
        max_length=255,
        verbose_name='Apellidos',
        null=True,  # Permitimos valores nulos
        blank=True 
    )
    document_number = models.CharField(
        max_length=20,
        verbose_name='Número de DNI o CE',
        null=True,  # Permitimos valores nulos
        blank=True 
    )

    # Campos opcionales para cuentas empresariales
    business_name = models.CharField(
        max_length=255,
        verbose_name='Razón Social',
        null=True,
        blank=True
    )
    ruc_number = models.CharField(
        max_length=20,
        verbose_name='Número de RUC',
        null=True,
        blank=True
    )
    legal_representative_name = models.CharField(
        max_length=255,
        verbose_name='Nombre del Representante Legal',
        null=True,
        blank=True
    )
    legal_representative_document = models.CharField(
        max_length=20,
        verbose_name='DNI o CE del Representante',
        null=True,
        blank=True
    )

    # Campos de la cuenta según el formulario de Perú
    account_number = models.CharField(
        max_length=255,
        verbose_name='Número de Cuenta',
        null=True,  # Permitimos valores nulos
        blank=True 
    )
    account_number_confirmation = models.CharField(
        max_length=255,
        verbose_name='Confirmar Número de Cuenta',
        null=True,  # Permitimos valores nulos
        blank=True 
    )
    
    # Campo opcional CCI según el formulario de Perú
    cci_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Número CCI'
    )
    cci_number_confirmation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Confirmar Número CCI'
    )

    # Campos específicos para Brasil según el formulario mostrado
    pix_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Clave PIX'
    )
    pix_key_confirmation = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Confirmar clave PIX'
    )
    pix_key_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Tipo de llave PIX'
    )
    cpf = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        verbose_name='CPF'
    )
    
    third_party = models.BooleanField(
       default=False,
       verbose_name='Cuenta de terceros'
   )
    # Campos de auditoría
    is_active = models.BooleanField(default=True)

    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPE_CHOICES,
        verbose_name='Tipo de Cuenta',
        null=True,
        blank=True
    )
    # Nuevo campo para moneda
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='bank_accounts',
        verbose_name='Moneda',
        null=True,
        blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Realizamos validaciones específicas según el país seleccionado.
        Para Perú verificamos la coincidencia de número de cuenta y CCI.
        Para Brasil verificamos la coincidencia de la clave PIX.
        """
        if self.country == 'PE':
            if self.account_number != self.account_number_confirmation:
                raise ValidationError('Los números de cuenta no coinciden')
            if self.cci_number and self.cci_number != self.cci_number_confirmation:
                raise ValidationError('Los números CCI no coinciden')
        
        elif self.country == 'BR':
            if self.pix_key != self.pix_key_confirmation:
                raise ValidationError('Las claves PIX no coinciden')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cuenta Bancaria'
        verbose_name_plural = 'Cuentas Bancarias'

    def __str__(self):
        """
        Representación en string que varía según el país
        """
        if self.country == 'PE':
            return f"{self.holder_names} {self.holder_surnames} - {self.bank_name}"
        return f"{self.holder_names} - PIX: {self.pix_key}"

class Coupon(models.Model):
    TYPE_CHOICES = (
        ('automatic', 'automatic'),
        ('manual', 'manual'),
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique coupon code (example: WELCOME10)",
        null=True,
        blank=True
    )
    
    description = models.TextField(
        help_text="Detailed description of the coupon and its conditions",
        null=True,
        blank=True
    )
    
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Discount percentage (0-100)",
        null=True,
        blank=True
    )
    
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the coupon becomes active",
        null=True,
        blank=True
    )
    
    end_date = models.DateTimeField(
        help_text="Date and time when the coupon expires",
        null=True,
        blank=True
    )
    
    source_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='source_coupons',
        help_text="Source currency for which the coupon applies",
        null=True,
        blank=True
    )
    
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='target_coupons',
        help_text="Target currency for which the coupon applies",
        null=True,
        blank=True
    )
    
    max_uses = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text="Maximum number of times the coupon can be used. Null means unlimited"
    )
    
    times_used = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the coupon has been used",
        null=True,
        blank=True
    )
    
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum transaction amount required to use the coupon"
    )
    
    image_cupon = models.ImageField(
        upload_to='coupons/',
        null=True,
        blank=True,
        help_text='Optional coupon image'
    )
    
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        null=True,
        blank=True,
        help_text='Coupon application type: automatic or manual'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the coupon is active or has been manually deactivated",
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% - {self.source_currency.code} → {self.target_currency.code})"   

class Transaction(models.Model):
    STATUS_CHOICES = (
    ('pending', 'Pendiente'),
    ('received', 'Recibido'),
    ('processing', 'En Proceso'), 
    ('observed', 'Observado'),
    ('completed', 'Finalizado'),
    ('cancelled', 'Cancelado')
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_transactions',
        verbose_name='Vendedor Asignado',
        blank=True 
    )

    transaction_id = models.CharField(max_length=50, unique=True)
    

    # Cuenta de origen y destino
    origin_account = models.ForeignKey(
        'transactions.BankAccount', 
        on_delete=models.CASCADE,
        related_name='origin_transactions',
        null=True,  
        blank=True 
    )
    destination_account = models.ForeignKey(
        'transactions.BankAccount', 
        on_delete=models.CASCADE,
        related_name='destination_transactions',
        null=True,  
        blank=True 
    )
    
    # Información de montos y tipo de cambio
    source_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monto que envía (ej: 1000 soles)
    source_currency = models.ForeignKey(
        'coin.Currency',
        on_delete=models.PROTECT,
        related_name='source_transactions',
        null=True,  
        blank=True 
    )
    
    destination_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Monto que recibe (ej: 300 dólares)
    destination_currency = models.ForeignKey(
        'coin.Currency',
        on_delete=models.PROTECT,
        related_name='destination_transactions',
        null=True,  
        blank=True 
    )
    
    #Informacion de Commission,  Taxes, Total to Send
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_send = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    #Informacion de cupon por descuento en Commission,  Taxes, Total to Send
    cupon_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cupon_taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cupon_total_send = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    #Informacion de descuento de cupon por recibir
    cupon_source_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cupon_destination_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    #rangos
    exchange_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        null=True,  
        blank=True )  # Tipo de cambio (ej: 1.25)
    
    # Resto de campos...
    payment_method = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_voucher = models.FileField(upload_to='vouchers/', null=True, blank=True)
    admin_voucher = models.FileField(
        upload_to='admin_vouchers/', 
        null=True, 
        blank=True,
        verbose_name='Admin Voucher Image'
    )
    
    coupon = models.ForeignKey(
        'transactions.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    reason_cancel = models.CharField(
        max_length=255,
        null=True,  
        blank=True 
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.source_amount} {self.source_currency} to {self.destination_amount} {self.destination_currency}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Obtener las iniciales de las monedas
            source_initial = self.source_currency.name[0]
            destination_initial = self.destination_currency.name[0]
            
            # Obtener la fecha actual en formato AAMMDD
            current_date = datetime.now().strftime('%y%m%d')
            
            # Contar transacciones del día actual
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            daily_count = Transaction.objects.filter(
                created_at__gte=today_start
            ).count()
            
            # Generar el número secuencial con 5 dígitos
            sequence = str(daily_count + 1).zfill(5)
            
            # Construir el transaction_id
            self.transaction_id = f"BRT-{source_initial}{destination_initial}{current_date}-{sequence}"
       
        # Asignar vendedor si es una nueva transacción
        if not self.pk and not self.seller:
            # Obtener todos los usuarios con rol sales o staff
            sellers = User.objects.filter(
                role__name__in=['sales', 'staff']
                #role__name__in=['sales']
            ).distinct()

            if sellers.exists():
                # Obtener la última transacción con vendedor asignado
                last_transaction = Transaction.objects.exclude(
                    seller__isnull=True
                ).order_by('-created_at').first()

                if last_transaction:
                    sellers_list = list(sellers)
                    try:
                        current_index = sellers_list.index(last_transaction.seller)
                        next_index = (current_index + 1) % len(sellers_list)
                        self.seller = sellers_list[next_index]
                    except ValueError:
                        self.seller = random.choice(sellers_list)
                else:
                    self.seller = random.choice(list(sellers))

                    
        super().save(*args, **kwargs)

