# Generated by Django 3.2.15 on 2022-09-30 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_alter_axiscreditcardstatements_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='axiscreditcardstatements',
            name='logs',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='axiscreditcardstatements',
            name='status',
            field=models.CharField(blank=True, choices=[('Unprocessed', 'Unprocessed'), ('Processing', 'Processing'), ('Processed', 'Processed'), ('Failed', 'Failed'), ('Cancelled', 'Cancelled')], default='Unprocessed', max_length=250, null=True),
        ),
    ]
