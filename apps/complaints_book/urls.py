from django.urls import path
from .views import ComplaintsBookListCreateView

urlpatterns = [
    path('', ComplaintsBookListCreateView.as_view(), name='complaints-list-create'),
]
