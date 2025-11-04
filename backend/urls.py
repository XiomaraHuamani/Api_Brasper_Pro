from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf.urls.static import static
from django.conf import settings


# Vista para la raíz
def home_view(request):
    return HttpResponse("Welcome to the API root")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("accounts/", include("allauth.urls")),
    # path('api/v1/auth/', include('apps.social_accounts.urls')),
    path("api/v1/coin/", include("apps.coin.urls")),
    # Ruta para libro de reclamaciones
    path("api/v1/complaints/", include("apps.complaints_book.urls")),
    path("api/v1/transactions/", include("apps.transactions.urls")),
    path("api/v1/company/", include("apps.company.urls")),
    path("api/v1/blogs/", include("apps.blogs.urls")),

    # Ruta para la raíz
    path("", home_view, name="home"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
