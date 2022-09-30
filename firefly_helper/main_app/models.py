from django.db import models
from django.core.validators import FileExtensionValidator

STATUS_CHOICES = [
    ('Unprocessed', 'Unprocessed'),
    ('Processing', 'Processing'),
    ('Processed', 'Processed'), 
    ('Failed', 'Failed'),
    ('Cancelled', 'Cancelled'),
]

STATEMENT_TYPES_CHOICES = [
    ('Axis CC', 'Axis CC'),
    ('Axis Savings', 'Axis Savings'),
    ('ICICI CC', 'ICICI CC'),
    ('ICICI Savings', 'ICICI Savings'),
    ('SBI CC', 'SBI CC'),
    ('SBI Savings', 'SBI Savings'),
]

# Create your models here.
class StatementFile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    files = models.FileField(upload_to='statement_uploads/',blank=True, null=True,validators=[FileExtensionValidator(allowed_extensions=["pdf","csv"])])
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default="Unprocessed", blank=True, null=True)
    processed_file = models.FileField(upload_to='processed_statements/', blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    statement_type = models.CharField(max_length=250, choices=STATEMENT_TYPES_CHOICES, default=None, blank=True, null=True)