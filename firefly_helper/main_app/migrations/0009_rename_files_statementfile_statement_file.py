# Generated by Django 3.2.15 on 2022-10-01 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0008_amazonorderdetail_amazonstatementfile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statementfile',
            old_name='files',
            new_name='statement_file',
        ),
    ]