# Generated by Django 5.1.5 on 2025-05-06 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_accountupgraderequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountupgraderequest',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='Pending', max_length=10),
        ),
    ]
