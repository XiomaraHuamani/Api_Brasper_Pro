from rest_framework import serializers
from .models import Currency, ExchangeRate, Commission, Range
from decimal import Decimal, InvalidOperation

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol', 'is_active', 'created_date', 'created_by']

class ExchangeRateSerializer(serializers.ModelSerializer):
    base_currency_name = serializers.CharField(source='base_currency.name', read_only=True)
    target_currency_name = serializers.CharField(source='target_currency.name', read_only=True)

    class Meta:
        model = ExchangeRate
        fields = [
            'id', 
            'base_currency',
            'base_currency_name',
            'target_currency',
            'target_currency_name',
            'rate',
            'created_date',
            'created_by',
            'updated_date',
            'updated_by'
        ]
        read_only_fields = ['updated_date']

    def validate_rate(self, value):
        if value is None:
            raise serializers.ValidationError("La tasa es requerida.")
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("La tasa debe ser un número válido.")
        if decimal_value <= 0:
            raise serializers.ValidationError("La tasa debe ser mayor que 0.")
        return value

    def validate(self, attrs):
        base = attrs.get('base_currency') or getattr(self.instance, 'base_currency', None)
        target = attrs.get('target_currency') or getattr(self.instance, 'target_currency', None)
        if base and target and base == target:
            raise serializers.ValidationError("La moneda base y la moneda objetivo deben ser distintas.")
        return attrs

class RangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Range
        fields = ['id', 'min_amount', 'max_amount', 'created_date', 'created_by']

class CommissionSerializer(serializers.ModelSerializer):
    base_currency_name = serializers.CharField(source='base_currency.name', read_only=True)
    target_currency_name = serializers.CharField(source='target_currency.name', read_only=True)
    range_details = RangeSerializer(source='range', read_only=True)

    class Meta:
        model = Commission
        fields = [
            'id',
            'base_currency',
            'base_currency_name',
            'target_currency',
            'target_currency_name',
            'range',
            'range_details',
            'commission_percentage',
            'reverse_commission',
            'created_date',
            'created_by'
        ]
        read_only_fields = ['created_date', 'created_by', 'id', 'range_details']

    def validate_commission_percentage(self, value):
        """Validar que commission_percentage sea un número válido entre 0 y 100"""
        if value is None:
            raise serializers.ValidationError("El porcentaje de comisión es requerido.")
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError("El porcentaje de comisión debe ser un número válido.")
        if decimal_value < 0 or decimal_value > 100:
            raise serializers.ValidationError("El porcentaje de comisión debe estar entre 0 y 100.")
        return decimal_value

    def validate_reverse_commission(self, value):
        """Validar que reverse_commission sea un número válido entre 0 y 100"""
        if value is None:
            raise serializers.ValidationError("La comisión inversa es requerida.")
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError("La comisión inversa debe ser un número válido.")
        if decimal_value < 0 or decimal_value > 100:
            raise serializers.ValidationError("La comisión inversa debe estar entre 0 y 100.")
        return decimal_value

    def validate(self, attrs):
        """Validación a nivel de objeto"""
        base = attrs.get('base_currency') or getattr(self.instance, 'base_currency', None)
        target = attrs.get('target_currency') or getattr(self.instance, 'target_currency', None)
        range_obj = attrs.get('range') or getattr(self.instance, 'range', None)
        
        if base and target and base == target:
            raise serializers.ValidationError({
                'base_currency': 'La moneda base y la moneda objetivo deben ser distintas.'
            })
        
        if range_obj is None:
            raise serializers.ValidationError({
                'range': 'El rango es requerido.'
            })
        
        return attrs

class ExchangeRateSerializerApp(serializers.ModelSerializer):
    base_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    target_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    base_currency_name = serializers.CharField(source='base_currency.name', read_only=True)
    target_currency_name = serializers.CharField(source='target_currency.name', read_only=True)

    class Meta:
        model = ExchangeRate
        fields = [
            'id', 
            'base_currency', 
            'base_currency_name',
            'target_currency',
            'target_currency_name',
            'rate'
        ]

    def validate_rate(self, value):
        if value is None:
            raise serializers.ValidationError("La tasa es requerida.")
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("La tasa debe ser un número válido.")
        if decimal_value <= 0:
            raise serializers.ValidationError("La tasa debe ser mayor que 0.")
        return value

    def validate(self, attrs):
        base = attrs.get('base_currency') or getattr(self.instance, 'base_currency', None)
        target = attrs.get('target_currency') or getattr(self.instance, 'target_currency', None)
        if base and target and base == target:
            raise serializers.ValidationError("La moneda base y la moneda objetivo deben ser distintas.")
        return attrs

    def to_representation(self, instance):
        return {
            f"{instance.base_currency.code}-{instance.target_currency.code}": instance.rate,
            'base_currency_name': instance.base_currency.name,
            'target_currency_name': instance.target_currency.name
        }

class RangeRateSerializerApp(serializers.Serializer):
    min = serializers.IntegerField(source='range.min_amount')
    max = serializers.IntegerField(source='range.max_amount')
    rate = serializers.FloatField(source='commission_percentage')

class CommissionSerializerApp(serializers.ModelSerializer):
    base_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    target_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    base_currency_name = serializers.CharField(source='base_currency.name', read_only=True)
    target_currency_name = serializers.CharField(source='target_currency.name', read_only=True)
    range = RangeRateSerializerApp(source='*')

    class Meta:
        model = Commission
        fields = [
            'base_currency',
            'base_currency_name',
            'target_currency',
            'target_currency_name',
            'range'
        ]

class ReverseRangeRateSerializerApp(serializers.Serializer):
    min = serializers.IntegerField(source='range.min_amount')
    max = serializers.IntegerField(source='range.max_amount')
    rate = serializers.DecimalField(max_digits=6, decimal_places=3, source='reverse_commission')

class ReverseCommissionSerializerApp(serializers.ModelSerializer):
    base_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    target_currency = serializers.SlugRelatedField(slug_field='code', queryset=Currency.objects.all())
    base_currency_name = serializers.CharField(source='base_currency.name', read_only=True)
    target_currency_name = serializers.CharField(source='target_currency.name', read_only=True)
    range = ReverseRangeRateSerializerApp(source='*')

    class Meta:
        model = Commission
        fields = [
            'base_currency',
            'base_currency_name',
            'target_currency',
            'target_currency_name',
            'range'
        ]