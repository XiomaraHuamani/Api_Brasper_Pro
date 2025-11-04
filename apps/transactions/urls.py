from django.urls import path
from .views import BankAccountListCreateView, BankAccountDetailView, CouponByCodeView, CouponDetailView, CouponManagementView, CouponV2ByCodeView, CouponV2DetailView, CouponV2ManagementView, CreateTransactionView, StaffTransactionDetailView, StaffTransactionListView, StaffTransactionStatusView, StaffTransactionVoucherView, TransactionDetailView, TransactionListView, CouponAutomaticView, CouponAutomaticDetailView

urlpatterns = [
    path('coupons/', CouponManagementView.as_view(), name='coupon-list-create'),
    path('coupons/<int:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/code/<str:code>/', CouponByCodeView.as_view(), name='coupon-by-code'),
    # V2 routes with extended fields (image_cupon, type)
    path('coupons/v2/', CouponV2ManagementView.as_view(), name='coupon-v2-list-create'),
    path('coupons/v2/<int:pk>/', CouponV2DetailView.as_view(), name='coupon-v2-detail'),
    path('coupons/v2/code/<str:code>/', CouponV2ByCodeView.as_view(), name='coupon-v2-by-code'),
    # Automatic coupons route (GET/POST, GET/PUT/PATCH by id)
    path('coupons/automatic/', CouponAutomaticView.as_view(), name='coupon-automatic'),
    path('coupons/automatic/<int:pk>/', CouponAutomaticDetailView.as_view(), name='coupon-automatic-detail'),
    path('bank-accounts/', BankAccountListCreateView.as_view(), name='bank-account-list-create'),
    path('bank-accounts/<int:pk>/', BankAccountDetailView.as_view(), name='bank-account-detail'),
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/',StaffTransactionListView.as_view(),name='transaction-list'),

    # Transaction steps - Following a logical flow for staff operations
    path('<int:pk>/review/',StaffTransactionDetailView.as_view(),name='transaction-review'),
    path('<int:pk>/update-status/',StaffTransactionStatusView.as_view(),name='transaction-status-update'),
    path('<int:pk>/upload-voucher/',StaffTransactionVoucherView.as_view(),name='transaction-voucher-upload'),

    #   Create Transaction
    path('transaction-create/',CreateTransactionView.as_view(),name='transaction-create-client'),

] 