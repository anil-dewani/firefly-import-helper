# Generated by Django 3.2.15 on 2022-10-09 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0022_amazonorderdetail_statement_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amazonorderdetail',
            name='order_id',
            field=models.CharField(max_length=250),
        ),
    ]
