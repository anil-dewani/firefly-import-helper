from django.contrib import admin
from main_app import models

# Register your models here.
@admin.register(models.StatementFile)
class StatementFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'files', 'status', 'processed_file','statement_type')
    list_filter = ('created_at','statement_type')
    date_hierarchy = 'created_at'