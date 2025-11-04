from django.db import models

# Create your models here.
class ComplaintsBook(models.Model):
    TYPE_PERSON_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
    ]
    
    TYPE_NONCONFORMITY_CHOICES = [
        ('claim', 'Claim'),
        ('complaint', 'Complaint'),
    ]

    date = models.DateField(auto_now_add=True)
    type_person = models.CharField(max_length=20)
    ruc = models.CharField(max_length=11)
    name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)
    email = models.EmailField()
    country_code = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=15)
    type_identity_document = models.CharField(max_length=50)
    identity_document_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    type_nonconformity = models.CharField(max_length=10, choices=TYPE_NONCONFORMITY_CHOICES)
    nonconformity_detail = models.TextField()
    order_nonconformity = models.CharField(max_length=100)
    file_upload = models.FileField(upload_to='uploads/', blank=True, null = True)

    def __str__(self):
        return f"{self.name} - {self.type_nonconformity}"