# Generated by Django 5.1.5 on 2025-05-07 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0010_flaggedtransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
    ]
