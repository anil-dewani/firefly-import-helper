# Generated by Django 3.2.15 on 2022-10-15 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0023_alter_amazonorderdetail_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='amazonstatementfile',
            name='selenoid_session_id',
            field=models.CharField(blank=True, default=None, max_length=250, null=True),
        ),
    ]
