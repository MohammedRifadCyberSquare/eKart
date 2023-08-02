# Generated by Django 4.2.3 on 2023-07-31 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_remove_deliveryaddress_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deliveryaddress',
            old_name='land_mark',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='deliveryaddress',
            old_name='pin_zode',
            new_name='pin_code',
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='district',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
