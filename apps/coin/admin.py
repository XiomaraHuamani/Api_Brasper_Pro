from django.contrib import admin
from .models import Currency, ExchangeRate, Range, Commission

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'is_active', 'created_date')
    list_filter = ('is_active', 'created_date')
    search_fields = ('code', 'name')
    readonly_fields = ('created_date', 'created_by')

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate', 'created_date')
    list_filter = ('base_currency', 'target_currency', 'created_date')
    search_fields = ('base_currency__code', 'target_currency__code')
    readonly_fields = ('created_date', 'created_by')

@admin.register(Range)
class RangeAdmin(admin.ModelAdmin):
    list_display = ('min_amount', 'max_amount', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('min_amount', 'max_amount')
    readonly_fields = ('created_date', 'created_by')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'range', 'commission_percentage', 'reverse_commission', 'created_date')
    list_filter = ('base_currency', 'target_currency', 'range', 'created_date')
    search_fields = ('base_currency__code', 'target_currency__code', 'range__min_amount', 'range__max_amount')
    readonly_fields = ('created_date', 'created_by')