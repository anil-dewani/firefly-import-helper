from django.contrib import admin
from main_app import models


@admin.register(models.StatementFile)
class StatementFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "statement_file",
        "status",
        "processed_file",
        "statement_type",
    )
    list_filter = ("created_at", "statement_type")
    date_hierarchy = "created_at"


@admin.register(models.AmazonStatementFile)
class AmazonStatementFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "statement_file",
        "selenoid_session_id",
        "status",
    )
    list_filter = ("created_at", "status")


@admin.register(models.AmazonOrderDetail)
class AmazonOrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_date",
        "order_id",
        "product_title",
        "order_amount",
        "product_link",
        "main_category",
        "category_list",
        "status",
    )
    list_filter = ("order_date", "status")


@admin.register(models.ProcessLog)
class ProcessLogAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "mode", "message")


# register admin for TransactionData
@admin.register(models.TransactionData)
class TransactionDataAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_date",
        "transaction_id",
        "description",
        "amount_debit",
        "amount_credit",
        "statement_file",
    )
    list_filter = ("asset_account", "category")
    search_fields = ("description", "transaction_id")
    date_hierarchy = "created_at"
