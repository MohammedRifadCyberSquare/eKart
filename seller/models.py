from django.db import models
from eKart_admin.models import Category
from customer.models import Seller



class Product(models.Model):
    product_no = models.CharField(max_length =  30)
    product_name =  models.CharField(max_length =  20)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete = models.CASCADE)
    description =  models.CharField(max_length =  200)
    stock = models.IntegerField()
    price = models.FloatField()
    image = models.ImageField(upload_to = 'product/')
    status = models.CharField(max_length = 20)
    
    class Meta:
        db_table = 'product_tb'