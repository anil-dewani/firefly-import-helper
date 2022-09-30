import os
from celery import Celery, shared_task
from celery import Task
from celery import signals
import psutil
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firefly_helper.settings')

#app = Celery('ecompanel',backend='amqp', broker="amqp://ecompanel_user:ecompanel420_@localhost:5672/")
app = Celery('ecompanel',broker="redis://:H5Bp7zhr9cperswCRTQ2PMVCxVRf@localhost:6379/7")
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if any("celery" in s for s in psutil.Process(os.getpid()).cmdline()):
    import django; django.setup()
    from main_app import models


@app.task()
def convert_statement_file(statement_id):
    """
    check statement type, extract data to put on universal csv file
    update statement file status
    done!
    """
    time.sleep(15)
    statement_file = models.StatementFile.objects.filter(id=statement_id).first()
    statement_file.status = "Processed"
    statement_file.save()
    return "Processed"

@app.task()
def convert_axis_cc_file():
    pass

@app.task()
def convert_axis_savings_file():
    pass