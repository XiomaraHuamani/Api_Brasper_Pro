from django.db import models

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
        related_name='base_currency',
        on_delete=models.CASCADE
    )
    target_currency = models.ForeignKey(
        Currency,
        related_name='target_currency',
        on_delete=models.CASCADE
    )
    rate = models.FloatField(
        null=True,
        default=1,
        help_text='Tasa de cambio entre la moneda base y la moneda objetivo'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )

    class Meta:
        unique_together = ('base_currency', 'target_currency')

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
    commission_percentage = models.FloatField(
        help_text='Porcentaje de comisión aplicado al intercambio de moneda'
    )
    reverse_commission = models.FloatField(
        help_text='Comisión inversa para el intercambio de moneda en dirección opuesta'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        default='',
        max_length=250,
        null=True
    )

    class Meta:
        unique_together = ('base_currency', 'target_currency', 'range')

    def __str__(self):
        return f"Commission from {self.base_currency.code} to {self.target_currency.code} ({self.range}): {self.commission_percentage}%"