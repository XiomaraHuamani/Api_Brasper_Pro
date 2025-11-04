from django.db import models
from django.utils import timezone
class PopupImage(models.Model):
    image_pe = models.FileField(upload_to='popups/', null=True, blank=True)
    image_br = models.FileField(upload_to='popups/', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    alias = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the popup becomes active"
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the popup expires"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the popup is active or has been manually deactivated"
    )
    class Meta:
        ordering = ['-created_at']