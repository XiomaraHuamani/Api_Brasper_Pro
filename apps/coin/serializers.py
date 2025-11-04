from rest_framework import serializers
from .models import Currency, ExchangeRate, Commission, Range

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
            'created_by'
        ]

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
        read_only_fields = ['created_date']

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
    rate = serializers.FloatField(source='reverse_commission')

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