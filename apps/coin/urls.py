from django.urls import path

from apps.users.views import RoleCreateView
from .views import (
    CommissionRangeView, CurrencyView, CurrencyDetailView,ReverseCommissionRatesViewApp,CommissionRatesViewApp,
    ExchangeRateView, ExchangeRateDetailView,
    CommissionView, CommissionDetailView,ReverseCommissionDetailViewApp,
    RangeView, RangeDetailView, ExchangeRateListViewApp, ExchangeRateDetailViewApp,  CommissionDetailViewApp
)

urlpatterns = [
    path('currencies/', CurrencyView.as_view(), name='currency-list'),
    path('currencies/<int:currency_id>/', CurrencyDetailView.as_view(), name='currency-detail'),
    # Rutas actualizadas para ExchangeRate
    path('exchange-rates-app/', ExchangeRateListViewApp.as_view(), name='exchange-rate-list'),
    #Error en la ejecución del endpoint: "'NoneType' object is not iterable"
    path('exchange-rates-app/<str:base_currency>-<str:target_currency>/', ExchangeRateDetailViewApp.as_view(), name='exchange-rate-detail'),
    #--------------
    # Rutas actualizadas para comission
    path('commission-rates-app/', CommissionRatesViewApp.as_view(), name='commission-rates'),
    path('reverse-commission-rates-app/', ReverseCommissionRatesViewApp.as_view(), name='reverse-commission-rates'),
    path('commissions-app/<str:base_currency>-<str:target_currency>/<int:min_amount>-<int:max_amount>/', 
         CommissionDetailViewApp.as_view(), name='commission-detail'),
    path('reverse-commissions-app/<str:base_currency>-<str:target_currency>/<int:min_amount>-<int:max_amount>/', 
         ReverseCommissionDetailViewApp.as_view(), name='reverse-commission-detail'),
    #--------------
    path('exchange-rates/', ExchangeRateView.as_view(), name='exchange-rate-list'),
    path('exchange-rates/<int:exchange_rate_id>/', ExchangeRateDetailView.as_view(), name='exchange-rate-detail'),
    path('ranges/', RangeView.as_view(), name='range-list'),
    path('ranges/<int:range_id>/', RangeDetailView.as_view(), name='range-detail'),
    path('commissions/', CommissionView.as_view(), name='commission-list'),
    path('commissions/<int:commission_id>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('commissions/ranges/', CommissionRangeView.as_view(), name='commission-ranges'),
]