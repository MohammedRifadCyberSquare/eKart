from django.shortcuts import render, redirect
from django.urls import reverse
from eKart_admin.models import Category
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import get_object_or_404  
from .models import Customer,Cart, DeliveryAddress, Order, OrderItem
from seller.models import Product, Seller
import razorpay
from django.utils.html import strip_tags
from datetime import datetime
from django.template.loader import render_to_string
from random import randint
from django.db.models import F
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def customer_home(request):
     
    return render(request, 'customer/customer_home.html',  )


def store(request):
    query = request.GET.get('query')
    
    if query == 'all':
        products = Product.objects.all()
     
    else:
         
        products = Product.objects.filter(category = query)
    count = products.count()

    context = {
        'products': products,
        'product_count': count
    }

    return render(request, 'customer/store.html', context)


def product_detail(request, product_id):
    seller = request.session['seller']
    message = ''
     
    product = Product.objects.get(id = product_id)
    customer = Customer.objects.get(id = request.session['customer'])
    product = None

    
    product = get_object_or_404(Product, id = product_id)
   
    
  

    if request.method == 'POST':
        cart = Cart(customer = customer, product = product, price = product.price)
        cart.save()
        return redirect('customer:cart',current_view = 'list')
             
   
    
    try:

        cart_item = get_object_or_404(Cart, customer = customer,product = product_id)
        item_exist = True
        


    except Exception as e:
         
        item_exist = False
         


    context = {
        'product': product,
        'item_exist': item_exist
    }    
   
    return render(request, 'customer/product_detail.html', context )


def cart(request, current_view):
    cart_items = Cart.objects.filter(customer = request.session['customer'])
    grand_total = 0
    customer = request.session['customer']
    disable_checkout = ''
    cart = Cart.objects.filter(customer = request.session['customer']).annotate(grand_total = F('quantity') * F('product__price') )
    
    for item in cart:
        grand_total += item.grand_total
    

    if not cart_items:
         disable_checkout = 'disabled'
    for item in cart_items:
       
         
        if item.product.stock == 0:
            disable_checkout = 'disabled'
            print(item.product.product_name,'not available')

     
    context = {
        'cart_items': cart_items, 
        'disable_checkout': disable_checkout, 
        'grand_total': grand_total,
        'total_items': cart_items.count(),
        
        }

    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        phone = request.POST['phone']
        email = request.POST['email']
        state = request.POST['state']
        landmark = request.POST['landmark']
        house = request.POST['house']
        zipcode = request.POST['pincode']
        delivery_address = DeliveryAddress(first_name = first_name, last_name = last_name, email = email,
                                           customer_id = customer,state = state, landmark = landmark, phone = phone, house_name = house, pin_code = zipcode)
        
        delivery_address.save()
        
    if current_view == 'review':
        try:
            address_history = DeliveryAddress.objects.filter(customer = customer)

        except Exception as e:
            print(e)
            address_history = None
        if address_history:
            print(address_history)
            context['address_history'] = address_history
        return render(request, 'customer/cart_review.html', context)
    

    return render(request, 'customer/cart.html', context)


def update_cart(request):
     
    product_id = request.POST['id']
    qty = request.POST['qty']
    print(qty)
    grand_total = 0
    cart = Cart.objects.get(product = product_id)
    cart.quantity = qty
    cart.save()

    cart = Cart.objects.filter(customer = request.session['customer']).annotate(grand_total = F('quantity') * F('product__price') )
    
    for item in cart:
        grand_total += item.grand_total
    
    # item_price = cart.product.price
    return JsonResponse({'status': 'Quantity updated', 'grand_total': grand_total})


def remove_cart_item(request, cart_id):

    try:
        selected_cart_item = Cart.objects.get(id = cart_id)
        selected_cart_item.delete()
    except:
        pass
    return redirect('customer:cart')


def review_cart(request):
    cart_items = Cart.objects.filter(customer = request.session['customer'])
    return render(request, 'customer/cart_review.html',{'cart_items': cart_items,})


def place_order(request):
    return render(request, 'customer/place_order.html')


def order_product(request):
    cart = Cart.objects.filter(customer = request.session['customer']).annotate(grand_total = F('quantity') * F('product__price') )

    customer = request.session['customer']
    grand_total = 0
    for item in cart:
       grand_total += item.grand_total
    
    order_amount = grand_total
    order_currency = 'INR'
    order_receipt ='order_rcptid_11'
    notes = {'shipping address':'bommanahalli,bangalore'}

     

    order_no = 'OD-Ekart-' + str(randint(1111111111,9999999999))
     
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY ,settings.RAZORPAY_API_SECRET))
    payment = client.order.create({
            'amount': order_amount * 100,
            'currency':order_currency,
            'receipt':order_receipt,
            'notes':notes,
             
        })
    
    order = Order(customer_id = customer, order_id = payment['id'], total_amount = grand_total, order_no = order_no )
    order.save()
    print(payment)
    return JsonResponse({'payment': payment})

@csrf_exempt
def update_payment(request, shipping_address):
    
    if request.method == 'GET':
        return redirect('customer:customer_home')

    order_id = request.POST['razorpay_order_id']
    payment_id = request.POST['razorpay_payment_id']
    signature = request.POST['razorpay_signature']
    client = razorpay.Client(auth = (settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        }
    signature_valid = client.utility.verify_payment_signature(params_dict)
    if signature_valid:
    
        order_details = Order.objects.get(order_id = order_id)
        order_details.payment_status = True
        order_details.payment_id = payment_id
        order_details.signature_id = signature
        order_details.shipping_address_id = shipping_address
        order_details.order_status = 'order placed'
        cart = Cart.objects.filter(customer = request.session['customer'])

        for item in cart:
            order_item = OrderItem(order_id = order_details.id, product_id = item.product.id, quantity = item.quantity, price = item.product.price )
            order_item.save()
            selected_qty = item.quantity
            selected_product = Product.objects.get(id = item.product.id)
            selected_product.stock -= selected_qty
            selected_product.save()
            

   
        order_details.save()
        cart.delete()

        customer_name = request.session['customer_name']
        order_number =  order_details.order_no
        current_year = datetime.now().year
        
        subject = "Order Confirmation"
        from_email = settings.EMAIL_HOST_USER

        to_email = ['athira@cybersquare.org']

        
        address = DeliveryAddress.objects.get(customer = request.session['customer'], id = shipping_address)
        html_content = render_to_string('customer/invoice.html', {
        'customer_name': customer_name,
        'order_no': order_number,
        'order_date': order_details.created_at,
        'current_year': current_year,
        'address': address,
        'grand_total': order_details.total_amount
        
        })
            
        msg = EmailMultiAlternatives(subject, html_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")

 
        msg.send()
    
    return render(request, 'customer/order_complete.html',  )


def dashboard(request):
    return render(request, 'customer/dashboard.html')


def seller_register(request):
    message = ''
    status = False
    if request.method == 'POST':  
        first_name = request.POST['fname'] 
        last_name = request.POST['lastname']
        email = request.POST['email']
        gender = request.POST['gender']
        company_name = request.POST['cmp_name']
        city = request.POST['city']
        country = request.POST['country']
        account_no = request.POST['acc_no']
        bank_name = request.POST['bank_name']
        branch = request.POST['branch']
        ifsc = request.POST['ifsc']
        pic = request.FILES['pic']
        




        
       
        seller_exist = Seller.objects.filter(email = email).exists()

        if not seller_exist: 

            seller = Seller(first_name = first_name, last_name = last_name, company_name = company_name,    gender = gender, email = email, 
                            city = city, country = country, account_no = account_no, bank_name = bank_name,
                            branch_name = branch, ifsc = ifsc, pic = pic)
            seller.save()
            message = 'Registration Succesful'
            status = True

        
        else:
            message = 'Email Exists'
    return render(request, 'customer/seller_register.html', {'message': message})


def seller_login(request):
    message = ''
    if request.method == 'POST':
        username = request.POST['seller_id']
        password = request.POST['password']

        seller = Seller.objects.filter(login_id = username, password = password)

        if seller.exists():
            request.session['seller'] = seller[0].id
            request.session['seller_name'] = seller[0].first_name + ' ' + seller[0].last_name
            return redirect('Seller:seller_home')

        else:

            message = 'Invalid Username Or Password'

    return render(request, 'customer/seller_login.html')


def customer_signup(request):
    message = ''
    status = False
    if request.method == 'POST':  
        first_name = request.POST['fname'] 
        last_name = request.POST['lastname']
        email = request.POST['email']
        gender = request.POST['gender']
        city = request.POST['city']
        country = request.POST['country']
        password = request.POST['password']

        
        
        customer_exist = Customer.objects.filter(email = email).exists()

        if not customer_exist: 

            customer = Customer(first_name = first_name, last_name = last_name, gender = gender, email = email, 
                            city = city, country = country, password = password)
            customer.save()
            message = 'Registration Succesful'
            status = True

        
        else:
            message = 'Email Exists'
   

    return render(request, 'customer/customer_signup.html', {'message': message, 'status': status})


def customer_login(request):

    message = ''

    if request.method == 'POST':


        email = request.POST['email']
        password = request.POST['password']

        customer = Customer.objects.filter(email = email, password = password)

        if customer.exists():
            request.session['customer'] = customer[0].id
            request.session['customer_name'] = customer[0].first_name

            return redirect('customer:customer_home')
        else:
            message = 'Username or Password Incorrect'

    return render(request, 'customer/customer_login.html', {'message': message,})


def forgot_password_customer(request):
    return render(request, 'customer/forgot_password_customer.html')


def forgot_password_seller(request):
    return render(request, 'customer/forgot_password_seller.html')

def my_orders(request):
    
    orders = Order.objects.filter(customer = request.session['customer'])
    return render(request, 'customer/my_orders.html', {'order_list': orders})
    
