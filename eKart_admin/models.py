from django.db import models

# Create your models here.

class EkartAdmin(models.Model):
    user_name = models.CharField(max_length = 20)
    password = models.CharField(max_length = 20)

    class Meta:
        db_table = 'admin_tb'