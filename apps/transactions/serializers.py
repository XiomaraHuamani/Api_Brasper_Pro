from datetime import timezone
from rest_framework import serializers
from .models import BankAccount, Coupon, Transaction
from apps.users.models import User

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id',
            'user',
            'country',
            'bank_name',
            'holder_names',
            'holder_surnames',
            'document_number',
            'business_name',
            'ruc_number',
            'legal_representative_name',
            'legal_representative_document',
            'account_number',
            'account_number_confirmation',
            'cci_number',
            'cci_number_confirmation',
            'cpf',
            'pix_key',
            'pix_key_confirmation',
            'pix_key_type',
            'third_party',
            'is_active',
            'account_type',
            'currency'
        ]
        
    def validate(self, data):
        """
        Validación personalizada que cambia según el país de la cuenta.
        Para cuentas peruanas, validamos número de cuenta y CCI.
        Para cuentas brasileñas, validamos CPF y clave PIX.
        """
        country = data.get('country')
        
        if country == 'PE':
            # Validaciones específicas para Perú
            if not data.get('account_number'):
                raise serializers.ValidationError({
                    'account_number': 'El número de cuenta es requerido para cuentas peruanas'
                })
            if data.get('account_number') != data.get('account_number_confirmation'):
                raise serializers.ValidationError({
                    'account_number_confirmation': 'Los números de cuenta no coinciden'
                })
            # El CCI es opcional, pero si se proporciona, debe coincidir
            if data.get('cci_number') and data.get('cci_number') != data.get('cci_number_confirmation'):
                raise serializers.ValidationError({
                    'cci_number_confirmation': 'Los números CCI no coinciden'
                })
            
        elif country == 'BR':
            # Validaciones específicas para Brasil
            if not data.get('cpf'):
                raise serializers.ValidationError({
                    'cpf': 'El CPF es requerido para cuentas brasileñas'
                })
            if not data.get('pix_key'):
                raise serializers.ValidationError({
                    'pix_key': 'La clave PIX es requerida para cuentas brasileñas'
                })
            if data.get('pix_key') != data.get('pix_key_confirmation'):
                raise serializers.ValidationError({
                    'pix_key_confirmation': 'Las claves PIX no coinciden'
                })
            # Removemos los campos que no aplican para Brasil
            data.pop('account_number', None)
            data.pop('account_number_confirmation', None)
            data.pop('cci_number', None)
            data.pop('cci_number_confirmation', None)

        return data

class CouponSerializer(serializers.ModelSerializer):
    """Legacy serializer without new fields for existing endpoints"""
    source_currency_code = serializers.CharField(source='source_currency.code', read_only=True)
    target_currency_code = serializers.CharField(source='target_currency.code', read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_percentage',
            'start_date', 'end_date', 'source_currency', 'target_currency',
            'source_currency_code', 'target_currency_code',
            'max_uses', 'times_used', 'minimum_amount', 'is_active','type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['times_used', 'created_at', 'updated_at']

class CouponV2Serializer(serializers.ModelSerializer):
    # Add currency codes for easier frontend handling
    source_currency_code = serializers.CharField(source='source_currency.code', read_only=True)
    target_currency_code = serializers.CharField(source='target_currency.code', read_only=True)
    image_cupon = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_percentage',
            'start_date', 'end_date', 'source_currency', 'target_currency',
            'source_currency_code', 'target_currency_code',
            'max_uses', 'times_used', 'minimum_amount',
            'image_cupon', 'type', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['times_used', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'end_date debe ser mayor que start_date'})
        return attrs

    def _normalize_empty_to_none(self, data: dict) -> dict:
        # Convert empty strings to None for nullable fields to avoid unique '' conflicts
        for field_name in ['code', 'description', 'type']:
            if data.get(field_name) == '':
                data[field_name] = None
        return data

    def create(self, validated_data):
        validated_data = self._normalize_empty_to_none(validated_data)
        # If code not provided or empty, leave as None so DB stores NULL (allowed with unique)
        if not validated_data.get('code'):
            validated_data['code'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._normalize_empty_to_none(validated_data)
        # Allow clearing the code by sending empty string
        if 'code' in validated_data and not validated_data['code']:
            validated_data['code'] = None
        return super().update(instance, validated_data)


class TransactionInitSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()  # Añadir este campo
    origin_account_id = serializers.IntegerField()
    destination_account_id = serializers.IntegerField()
    source_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    destination_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    exchange_rate = serializers.DecimalField(max_digits=10, decimal_places=6)

class TransactionConfirmSerializer(serializers.Serializer):
    voucher = serializers.FileField(required=False)

class TransactionSerializer(serializers.ModelSerializer):
   class Meta:
       model = Transaction 
       fields = [
           'id',
           'user',
           'seller',
           'transaction_id',
           'origin_account',
           'destination_account',
           'source_amount',
           'source_currency',
           'destination_amount', 
           'destination_currency',
           'exchange_rate',
           'payment_method',
           'status',
           'payment_voucher',
           'admin_voucher',
           'coupon',
           'created_at',
           'updated_at'
       ]
       read_only_fields = ['id', 'transaction_id', 'created_at', 'updated_at']

   def validate(self, data):
        """
        Validaciones adicionales
        """
        if data['origin_account'] == data['destination_account']:
            raise serializers.ValidationError(
                "Las cuentas de origen y destino no pueden ser la misma"
            )


        return data
   
class StaffTransactionSerializer(serializers.ModelSerializer):
    # Custom read-only fields to display related information
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    
    # Account details as readable strings
    origin_account_details = serializers.SerializerMethodField()
    destination_account_details = serializers.SerializerMethodField()
    
    # Currency codes for easier display
    source_currency_code = serializers.CharField(source='source_currency.code', read_only=True)
    destination_currency_code = serializers.CharField(source='destination_currency.code', read_only=True)
    seller_details = serializers.SerializerMethodField()  # Agregar esta línea

    # Optional coupon code display
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'user',
            'user_email',
            'user_full_name',
            'seller',
            'seller_details',
            'origin_account',
            'origin_account_details',
            'destination_account',
            'destination_account_details',
            'source_amount',
            'source_currency',
            'source_currency_code',
            'destination_amount',
            'destination_currency',
            'destination_currency_code',
            'commission',
            'taxes',
            'total_send',
            'cupon_commission',
            'cupon_taxes',
            'cupon_total_send',
            'cupon_source_amount',
            'cupon_destination_amount',
            'exchange_rate',
            'payment_method',
            'status',
            'payment_voucher',
            'admin_voucher',
            'coupon',
            'coupon_code',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'created_at', 'updated_at']
    
    def get_seller_details(self, obj):
        if obj.seller:
                return {
                    'id': obj.seller.id,
                    'email': obj.seller.email,
                    'full_name': f"{obj.seller.first_name} {obj.seller.last_name}".strip(),
                    'username': obj.seller.username
                }
        return None
    def get_user_full_name(self, obj):
        """Returns the full name of the user who created the transaction"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email

    def get_account_details(self, account):
        if not account:
            return None

        # Datos base que comparten ambos países
        details = {
            'bank_name': account.bank_name,
            'currency': {
                'id': account.currency.id if account.currency else None,
                'name': account.currency.name if account.currency else None,
                'code': account.currency.code if account.currency else None,
                'symbol': account.currency.symbol if account.currency else None
            },
            'account_type': account.get_account_type_display(),
            'third_party': account.third_party,
            'country': account.country
        }

        # Datos específicos según el país
        if account.country == 'PE':
            details.update({
                'holder_names': account.holder_names,
                'holder_surnames': account.holder_surnames,
                'document_number': account.document_number,
                'account_number': account.account_number,
                'cci_number': account.cci_number
            })
        elif account.country == 'BR':
            details.update({
                'holder_names': account.holder_names,
                'holder_surnames': account.holder_surnames,
                'document_number': account.document_number,
                'account_number': account.account_number,
                'pix_key': account.pix_key,
                'pix_key_type': account.pix_key_type,
                'cpf': account.cpf
            })

        return details

    def get_origin_account_details(self, obj):
        return self.get_account_details(obj.origin_account)

    def get_destination_account_details(self, obj):
        return self.get_account_details(obj.destination_account)
    def validate(self, data):
        """
        Custom validation logic for staff transactions
        """
        # Validate coupon if provided
        if 'coupon' in data and data['coupon']:
            coupon = data['coupon']
            if not coupon.is_active:
                raise serializers.ValidationError({
                    'coupon': 'El cupón no está activo'
                })
            if coupon.valid_until and coupon.valid_until < timezone.now():
                raise serializers.ValidationError({
                    'coupon': 'El cupón ha expirado'
                })



        # Validate amounts are positive
        if 'source_amount' in data and data['source_amount'] <= 0:
            raise serializers.ValidationError({
                'source_amount': 'El monto de origen debe ser mayor a 0'
            })

        if 'destination_amount' in data and data['destination_amount'] <= 0:
            raise serializers.ValidationError({
                'destination_amount': 'El monto de destino debe ser mayor a 0'
            })

        return data 

class TransactionResponseSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    payment_voucher = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'transaction_id',
            'source',
            'destination',
            'exchange_rate',
            'payment_method',
            'status',
            'payment_voucher',
            'created_at'
        ]

    def get_source(self, obj):
        return {
            'amount': str(obj.source_amount),
            'currency': obj.source_currency.code,
            'account': obj.origin_account.id
        }

    def get_destination(self, obj):
        return {
            'amount': str(obj.destination_amount),
            'currency': obj.destination_currency.code,
            'account': obj.destination_account.id
        }

    def get_payment_voucher(self, obj):
        if obj.payment_voucher:
            return self.context['request'].build_absolute_uri(obj.payment_voucher.url)
        return None