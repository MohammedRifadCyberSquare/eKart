# Generated by Django 4.2.3 on 2023-08-11 09:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0025_alter_orderitem_delivered_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='cancelled_date',
            field=models.DateField(default=datetime.date.today, null=True),
        ),
    ]
