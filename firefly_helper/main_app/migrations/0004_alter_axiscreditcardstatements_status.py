# Generated by Django 3.2.15 on 2022-09-30 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_auto_20220930_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='axiscreditcardstatements',
            name='status',
            field=models.CharField(blank=True, choices=[('Unprocessed', 'Unprocessed'), ('Processing', 'Processing'), ('Processed', 'Processed'), ('Failed', 'Failed')], default='Unprocessed', max_length=250, null=True),
        ),
    ]