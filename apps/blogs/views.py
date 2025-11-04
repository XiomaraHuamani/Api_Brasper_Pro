from rest_framework import viewsets
from .models import Blog
from .serializers import BlogSerializer
from apps.users.permissions import IsStaff
from rest_framework.permissions import AllowAny

    
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-date')
    serializer_class = BlogSerializer
    lookup_field = 'slug' 
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]
