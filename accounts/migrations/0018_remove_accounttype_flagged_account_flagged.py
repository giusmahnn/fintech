# Generated by Django 5.1.5 on 2025-05-07 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_accounttype_flagged'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounttype',
            name='flagged',
        ),
        migrations.AddField(
            model_name='account',
            name='flagged',
            field=models.BooleanField(default=False),
        ),
    ]
