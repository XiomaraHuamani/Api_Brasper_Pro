from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.permissions import IsStaff
from .models import ComplaintsBook
from .serializers import ComplaintsBookSerializer
from rest_framework.permissions import AllowAny
class ComplaintsBookListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()] 
        elif self.request.method == 'POST':
            return [IsStaff()]  # Requiere autenticación
        return super().get_permissions()
    def get(self, request):
        complaints = ComplaintsBook.objects.all()
        serializer = ComplaintsBookSerializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ComplaintsBookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

