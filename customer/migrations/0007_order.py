# Generated by Django 4.2.3 on 2023-08-01 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_deliveryaddress_landmark'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=25, unique=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_id', models.CharField(max_length=25, null=True, unique=True)),
                ('signature', models.CharField(max_length=250, null=True, unique=True)),
                ('order_status', models.CharField(max_length=20, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer')),
            ],
            options={
                'db_table': 'order_tb',
            },
        ),
    ]