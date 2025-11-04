from django.db import models
from django.utils.translation import gettext_lazy as _

class LanguageChoices(models.TextChoices):
    ES = 'es', _('Español')
    EN = 'en', _('Inglés')
    PT = 'pt', _('Portugués')

class Blog(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=False)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True, null=True)  # ID de Cloudinary
    read_time = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ES
    )
    def __str__(self):
        return self.title or "Sin título"
