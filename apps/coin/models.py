from django.db import models
from django.db.models import Q, F

class Currency(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text='Código de la moneda, por ejemplo, USD, EUR'
    )
    name = models.CharField(
        max_length=100,
        help_text='Nombre completo de la moneda, por ejemplo, Dólar Estadounidense'
    )
    symbol = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Símbolo de la moneda, por ejemplo, $ o €'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la moneda está activa o no'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

class ExchangeRate(models.Model):
    id = models.BigAutoField(primary_key=True)
    base_currency = models.ForeignKey(
        Currency,
        related_name='as_base_rates',
        on_delete=models.CASCADE,
        db_index=True
    )
    target_currency = models.ForeignKey(
        Currency,
        related_name='as_target_rates',
        on_delete=models.CASCADE,
        db_index=True
    )
    rate = models.DecimalField(max_digits=20, decimal_places=8, default=1, help_text='Tasa base→objetivo')
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )
    updated_date = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(
        default='',
        max_length=250,
        null=True,
        help_text='Usuario que realizó la última actualización'
    )

    class Meta:
        ordering = ['-created_date']
        get_latest_by = 'created_date'
        constraints = [
            models.UniqueConstraint(fields=['base_currency', 'target_currency'], name='uniq_base_target'),
            models.CheckConstraint(check=Q(rate__gt=0), name='rate_gt_zero'),
            models.CheckConstraint(check=~Q(base_currency=F('target_currency')), name='base_ne_target'),
        ]
        indexes = [
            models.Index(fields=['base_currency', 'created_date'], name='idx_base_created'),
            models.Index(fields=['target_currency', 'created_date'], name='idx_target_created'),
        ]

    def __str__(self):
        return f"{self.base_currency.code} to {self.target_currency.code}: {self.rate}"

class Range(models.Model):
    id = models.BigAutoField(primary_key=True)
    min_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text='Cantidad mínima del rango'
    )
    max_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text='Cantidad máxima del rango'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )

    def __str__(self):
        return f"Range: {self.min_amount} - {self.max_amount}"

    class Meta:
        unique_together = ('min_amount', 'max_amount')

class Commission(models.Model):
    id = models.BigAutoField(primary_key=True)
    base_currency = models.ForeignKey(
        Currency,
        related_name='commission_base_currency',
        on_delete=models.CASCADE
    )
    target_currency = models.ForeignKey(
        Currency,
        related_name='commission_target_currency',
        on_delete=models.CASCADE
    )
    range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        related_name='commissions',
        help_text='Rango de cantidad asociado a esta comisión'
    )
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text='Porcentaje de comisión aplicado al intercambio de moneda')
    reverse_commission = models.DecimalField(max_digits=5, decimal_places=2, help_text='Comisión inversa para el intercambio de moneda en dirección opuesta')
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['base_currency', 'target_currency', 'range'], name='uniq_commission_triplet'),
            models.CheckConstraint(check=Q(commission_percentage__gte=0) & Q(commission_percentage__lte=100), name='commission_pct_0_100'),
            models.CheckConstraint(check=Q(reverse_commission__gte=0) & Q(reverse_commission__lte=100), name='reverse_commission_0_100'),
        ]
        indexes = [
            models.Index(fields=['base_currency', 'target_currency', 'range'], name='idx_comm_base_target_range'),
        ]

    def __str__(self):
        return f"Commission from {self.base_currency.code} to {self.target_currency.code} ({self.range}): {self.commission_percentage}%"