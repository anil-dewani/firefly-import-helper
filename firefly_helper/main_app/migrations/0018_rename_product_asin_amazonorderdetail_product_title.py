# Generated by Django 3.2.15 on 2022-10-02 16:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0017_auto_20221002_0128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='amazonorderdetail',
            old_name='product_asin',
            new_name='product_title',
        ),
    ]
