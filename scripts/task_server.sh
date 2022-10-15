export CELERY_BROKER_URL=redis://127.0.0.1:6380/0;
cd ./firefly_helper/
watchfiles celery.__main__.main --args '-A main_app.celery worker -l INFO'
