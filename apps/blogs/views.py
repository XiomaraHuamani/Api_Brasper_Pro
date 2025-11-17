from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Blog
from .serializers import BlogSerializer, BlogListSerializer
from apps.users.permissions import IsStaff
from rest_framework.permissions import AllowAny

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@method_decorator(cache_page(60), name='list')
@method_decorator(cache_page(60), name='retrieve')
class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    lookup_field = 'slug'
    pagination_class = BlogPagination

    def get_queryset(self):
        base_qs = Blog.objects.all()
        if self.action == 'list':
            # Evita traer el campo pesado 'content' en listados
            return (
                base_qs
                .only('id', 'title', 'slug', 'excerpt', 'category', 'public_id', 'read_time', 'date', 'language')
                .order_by('-date')
            )
        return base_qs.order_by('-date')

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogListSerializer
        return BlogSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]
