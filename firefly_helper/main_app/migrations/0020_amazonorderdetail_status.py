# Generated by Django 3.2.15 on 2022-10-02 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0019_auto_20221002_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='amazonorderdetail',
            name='status',
            field=models.CharField(choices=[('Unprocessed', 'Unprocessed'), ('Processing', 'Processing'), ('Processed', 'Processed'), ('Failed', 'Failed'), ('Cancelled', 'Cancelled')], default='Unprocessed', max_length=250),
        ),
    ]
