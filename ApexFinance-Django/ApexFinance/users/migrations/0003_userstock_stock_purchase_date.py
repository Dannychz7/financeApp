# Generated by Django 5.1.2 on 2024-10-22 18:13

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_account_balance_profile_available_cash'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstock',
            name='stock_purchase_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
