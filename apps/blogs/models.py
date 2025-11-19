from django.db import models
from django.utils.translation import gettext_lazy as _

class LanguageChoices(models.TextChoices):
    ES = 'es', _('Español')
    EN = 'en', _('Inglés')
    PT = 'pt', _('Portugués')

class Blog(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=500, blank=True, null=False)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    public_id = models.CharField(max_length=255, blank=True, null=True)  # ID de Cloudinary
    read_time = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(auto_now_add=True, db_index=True)
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ES,
        db_index=True
    )

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date'], name='blog_date_desc_idx'),
            models.Index(fields=['language', '-date'], name='blog_lang_date_idx'),
            models.Index(fields=['category', '-date'], name='blog_cat_date_idx'),
        ]

    def __str__(self):
        return self.title or "Sin título"
