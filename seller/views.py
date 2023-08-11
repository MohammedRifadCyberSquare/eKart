from django.shortcuts import render,redirect
from eKart_admin.models import Category
from django.core.exceptions import ObjectDoesNotExist
from .models import Seller
from datetime import date

from customer.models import OrderItem
from django.db.models import Q
from django.http import JsonResponse
from seller.models import Product


# Create your views here.
def seller_home(request):
    products = Product.objects.filter(seller = request.session['seller']).count()
    orders = OrderItem.objects.filter(product__seller = request.session['seller'], status = 'order placed').count()
    context = {
        'product_count': products,
        'orders': orders
    }
    return render(request, 'seller/seller_home.html', context)

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

def change_password(request):
    status_msg = ''
    if request.method  == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        try:
            if len(new_password) > 8:
                if new_password == confirm_password:
                    seller = Seller.objects.get(id = request.session['seller'])
                    if seller.password == old_password:
                        seller.password = new_password
                        seller.save()
                        status_msg = 'Password Changed'

                    else:
                        status_msg = 'Password Incorrect'
                else:
                    status_msg = 'Password Does Not Match'
            else:
                status_msg = 'Password Should Be Minimum 8 Characters'


        except:
            status_msg = 'Incorrect Password'
    return render(request, 'seller/change_password.html', {'msg': status_msg})

def view_orders(request):

    return render(request,'seller/view_orders.html')

def update_stock(request):

    product_list = Product.objects.filter(seller = request.session['seller']).values('id','product_no','product_name')
    print(product_list, '999')
    if request.method == 'POST':
        product_id= request.POST['productId']
        new_stock = request.POST['newStock']

        print(product_id, new_stock)

        selected_product = Product.objects.get(id = product_id, seller = request.session['seller']) 
        new_stock = selected_product.stock + int(new_stock)
        selected_product.stock = new_stock
        selected_product.save()

        return JsonResponse({'status': True, 'updated_stock': new_stock})


    return render(request,'seller/update_stock.html', {'list': product_list})

def get_stock_details(request):
    product_id = request.POST['productId']
    product = Product.objects.filter(id = product_id).values('product_name','stock')
    product_name = product[0]['product_name']
    current_stock = product[0]['stock']
    return JsonResponse({'product_name': product_name, 'stock': current_stock})

def update_order_status(request, order_id):
   pass

def recent_orders(request):
    
    orders = OrderItem.objects.filter(~Q(status = 'delivered'),product__seller = request.session['seller'] )
    if request.method == 'POST':
        try:
            print('uuu')
            order_status = request.POST['status'] 
            order_id = request.POST['order_id'] 

            order_item = OrderItem.objects.get(id = order_id)  
            if order_status == 'delivered':
                order_item.delivered_date = date.today()
            
            if order_status == 'packed':
                order_item.packed_date = date.today()

            if order_status == 'out for delivery':
                order_item.delivery_out = date.today()
            order_item.status = order_status
            order_item.save()

             
        except Exception as e:
            print(e)
            None
    return render(request,'seller/recent_orders.html', {'items': orders})

def order_history(request):
    return render(request,'seller/order_history.html')

def order_items(request, order_no):
    items = OrderItem.objects.filter(order__order_no = order_no, product__seller = request.session['seller'] )
    order_no = items[0].order.order_no
    if request.method == 'POST':
        try:
             
            order_status = request.POST['status'] 
            order_id = request.POST['order_id'] 

            print(order_status)
            order_item = OrderItem.objects.get(id = order_id)  
            if order_status == 'delivered':
                order_item.delivered_date = date.today()

            if order_status == 'packed':
                order_item.packed_date = date.today()

            if order_status == 'out for delivery':
                order_item.delivery_out = date.today()
             
            order_item.status = order_status
            order_item.save()

             
        except Exception as e:
            print(e)
            None
    return render(request,'seller/order_items.html', {'items': items, 'order_no': order_no})
