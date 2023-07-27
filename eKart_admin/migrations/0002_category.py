# Generated by Django 4.2.3 on 2023-07-27 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eKart_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('cover_pic', models.ImageField(upload_to='category/')),
            ],
            options={
                'db_table': 'category_tb',
            },
        ),
    ]
