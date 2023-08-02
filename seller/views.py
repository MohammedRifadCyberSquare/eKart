from django.shortcuts import render
from eKart_admin.models import Category
from django.core.exceptions import ObjectDoesNotExist
from .models import Seller
from django.http import JsonResponse
from seller.models import Product


# Create your views here.
def seller_home(request):
    return render(request, 'seller/seller_home.html')

def add_product(request):
    category_list = Category.objects.all()
    message = ''

    if request.method == 'POST':
        product_no = request.POST['product_code']
        product_name = request.POST['product_name']
        category = request.POST['category']
        description = request.POST['description']
        stock = request.POST['stock']
        price = request.POST['price']
        image = request.FILES['image']
        seller = request.session['seller']
        

       
             
        product, created = Product.objects.get_or_create(product_no = product_no, seller = seller, defaults = {
            'product_no': product_no, 
            'product_name': product_name.lower(),
            'seller': Seller.objects.get(id = seller),
            'category': Category.objects.get(id = category),
            'description': description.lower(),
            'stock': stock,
            'price': price,
            'image': image,
        })

        if created:
            print('added')
            message = 'Product Added'
        
        else:
            print('else')
            message = 'Product No Already exists'

       

    context = {
        'category': category_list,
        'message': message
    }
    return render(request, 'seller/add_product.html', context)

def add_category(request):
    return render(request, 'seller/add_category.html')

def view_category(request):
    return render(request, 'seller/view_category.html')

def view_products(request):
    products = Product.objects.filter(seller = request.session['seller'])
    return render(request, 'seller/product_catalogue.html', {'products': products,})

def profile(request):
    return render(request,'seller/profile.html')

def view_orders(request):
    return render(request,'seller/view_orders.html')

def update_stock(request):

    if request.method == 'POST':
        product_no = request.POST['productNo']
        new_stock = request.POST['newStock']

        print(product_no, new_stock)

        selected_product = Product.objects.get(product_no = product_no, seller = request.session['seller']) 
        new_stock = selected_product.stock + int(new_stock)
        selected_product.stock = new_stock
        selected_product.save()

        return JsonResponse({'status': True, 'updated_stock': new_stock})


    return render(request,'seller/update_stock.html')

def get_stock_details(request):
    product_no = request.POST['productNo']
    product = Product.objects.filter(product_no = product_no, seller = request.session['seller']).values('product_name','stock')
    if product:
        product_name = product[0]['product_name']
        current_stock = product[0]['stock']
        return JsonResponse({'product_exist': True,'product_name': product_name, 'stock': current_stock})
    else:
        print(product_no, 'does not exist')
        return JsonResponse({'product_exist': False,})

def order_history(request):
    return render(request,'seller/order_history.html')