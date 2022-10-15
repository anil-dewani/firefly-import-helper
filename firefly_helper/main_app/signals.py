from django.db.models.signals import post_save
from django.dispatch import receiver
from main_app import models
from main_app import celery




@receiver(post_save, sender=models.TransactionData)
def filter_amazon_transactions(sender, instance, created, **kwargs):
    if created:
        if "amazon" in instance.description.lower():
            instance.status = "Processing"
            instance.save()
            celery.process_amazon_transaction.apply_async((instance.statement_file.id, instance.id))
            celery.log_message("INFO", "Amazon Transaction Detected with Amount : "+str(instance.amount_debit)+" or "+str(instance.amount_credit),instance.statement_file.id)
            