from django.shortcuts import render, redirect
from eKart_admin.models import Category
from django.shortcuts import get_object_or_404  
from .models import Customer,Cart
from seller.models import Product, Seller
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
        cart = Cart(customer = customer, product = product)
        cart.save()
        return redirect('customer:cart')
             
   
    
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


def cart(request):
    cart_items = Cart.objects.filter(customer = request.session['customer'])
    grand_total = 0
    
    disable_checkout = False
    for item in cart_items:
        print(item.product.product_name, item.product.stock)
        grand_total += item.product.price
        if item.product.stock == 0:
            disable_checkout = True
            print(item.product.product_name,'not available')

    context = {
        'cart_items': cart_items, 
        'disable_checkout': disable_checkout, 
        'grand_total': grand_total,
        'total_items': cart_items.count()
        }  
    return render(request, 'customer/cart.html', context)


def place_order(request):
    return render(request, 'customer/place_order.html')


def order_complete(request):
    return render(request, 'customer/order_complete.html')


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