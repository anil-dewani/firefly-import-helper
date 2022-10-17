from django.core.validators import FileExtensionValidator
from django.db import models

STATUS_CHOICES = [
    ("Unprocessed", "Unprocessed"),
    ("Processing", "Processing"),
    ("Processed", "Processed"),
    ("Failed", "Failed"),
    ("Cancelled", "Cancelled"),
]

STATEMENT_TYPES_CHOICES = [
    ("Axis CC", "Axis CC"),
    ("Axis Savings", "Axis Savings"),
    ("ICICI CC", "ICICI CC"),
    ("ICICI Savings", "ICICI Savings"),
    ("SBI CC", "SBI CC"),
    ("SBI Savings", "SBI Savings"),
    ("Amazon Mapping Data", "Amazon Mapping Data"),
]

LOG_DATA_MODES = [
    ("INFO", "INFO"),
    ("WARNING", "WARNING"),
    ("ERROR", "ERROR"),
    ("DEBUG", "DEBUG"),
]


class ProcessLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(choices=LOG_DATA_MODES, default="INFO", max_length=100)
    message = models.TextField(blank=True, null=True)


class StatementFile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    statement_file = models.FileField(
        upload_to="statement_uploads/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "csv", "xls"])],
    )
    status = models.CharField(
        max_length=250,
        choices=STATUS_CHOICES,
        default="Unprocessed",
        blank=True,
        null=True,
    )
    processed_file = models.FileField(
        upload_to="processed_statements/", blank=True, null=True
    )
    statement_type = models.CharField(
        max_length=250,
        choices=STATEMENT_TYPES_CHOICES,
        default=None,
        blank=True,
        null=True,
    )
    log_data = models.ManyToManyField(ProcessLog, null=True, blank=True)


class AmazonStatementFile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    statement_file = models.FileField(
        upload_to="amazon_statement_uploads/",
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
    )
    status = models.CharField(
        max_length=250,
        choices=STATUS_CHOICES,
        default="Unprocessed",
        blank=True,
        null=True,
    )
    log_data = models.ManyToManyField(ProcessLog, null=True, blank=True)
    selenoid_session_id = models.CharField(
        max_length=250, default=None, null=True, blank=True
    )


class AmazonOrderDetail(models.Model):
    order_date = models.DateTimeField(blank=True, null=True)
    order_id = models.CharField(max_length=250)
    product_title = models.CharField(max_length=250)
    order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    product_link = models.CharField(max_length=100, null=True, blank=True, default=None)
    main_category = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    category_list = models.CharField(
        max_length=250, null=True, blank=True, default=None
    )
    json_data = models.TextField(blank=True, null=True, default=None)
    status = models.CharField(
        max_length=250, choices=STATUS_CHOICES, default="Unprocessed"
    )
    statement_file = models.ForeignKey(
        AmazonStatementFile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )


class TransactionData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_date = models.DateField()
    transaction_id = models.CharField(
        max_length=250, blank=True, null=True, default=None
    )
    asset_account = models.CharField(
        max_length=250, blank=True, null=True, default=None
    )
    amount_credit = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    amount_debit = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=None
    )
    description = models.CharField(max_length=250)
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=250, blank=True, null=True, default=None)
    category = models.CharField(max_length=250, blank=True, null=True, default=None)
    statement_file = models.ForeignKey(StatementFile, on_delete=models.CASCADE)
    status = models.CharField(
        choices=STATUS_CHOICES, default="Unprocessed", max_length=100
    )
