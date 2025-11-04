from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PopupImage
from .serializers import PopupImageSerializer
from rest_framework.permissions import AllowAny

class PopupImageView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView
):
    queryset = PopupImage.objects.all()
    serializer_class = PopupImageSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        # Tomamos el primero según el orden definido en el modelo (último creado)
        return PopupImage.objects.first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({'error': 'No popup image found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        image_pe = request.FILES.get('image_pe')
        image_br = request.FILES.get('image_br')

        if not image_pe or not image_br:
            return Response(
                {'error': 'Both image_pe and image_br are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrar anteriores
        PopupImage.objects.all().delete()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'error': 'No popup image found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'error': 'No popup image found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'error': 'No popup image found'}, status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response({'message': 'Popup image deleted'}, status=status.HTTP_204_NO_CONTENT)