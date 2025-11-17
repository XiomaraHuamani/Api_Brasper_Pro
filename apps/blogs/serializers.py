from rest_framework import serializers
from .models import Blog, LanguageChoices

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'slug',
            'excerpt',
            'category',
            'public_id',
            'read_time',
            'date',
            'language',
        ]

    def validate_language(self, value):
        """
        Valida que el idioma sea uno de los soportados.
        """
        if value not in LanguageChoices.values:
            raise serializers.ValidationError(f"Idioma no soportado: {value}")
        return value

