from django.shortcuts import render, redirect
from django.urls import reverse
from eKart_admin.models import Category
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import get_object_or_404  
from .models import *
from .rating import *
from datetime import date
from django.db.models import Count,ExpressionWrapper,FloatField
from seller.models import Product, Seller
import razorpay
from django.utils.html import strip_tags
from datetime import datetime
from django.template.loader import render_to_string
from random import randint
from django.db.models import F
from django.core.serializers import serialize
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
    product = Product.objects.get(id = product_id)
    already_reviewed = False
    try:
        customer = Customer.objects.get(id = request.session['customer'])
        already_reviewed = ProductReview.objects.filter(customer = customer, product = product_id).exists()
    
    except:
        None
    product = None

    questions = ProductQuestion.objects.filter(product = product_id)
    product = get_object_or_404(Product, id = product_id)

    reviews =  ProductReview.objects.filter(product = product_id)
    product_rating =reviews.values('rating').annotate(count = Count('rating'))
   
    
     
    rating_list = get_rating(product_id)

    review_count = ProductReview.objects.filter(product = product_id).count()
    
    
    star_rating = get_star_rating(rating_list)
    if request.method == 'POST':
        if 'customer' in request.session:
            cart = Cart(customer = customer, product = product, price = product.price)
            cart.save()
            return redirect('customer:cart',current_view = 'list')
        
        else:
            target_url = reverse('customer:customer_login')
             
            redirect_url =  target_url + '?pid=' + str(product_id)
            return redirect(redirect_url)
             
   
    
    try:

        cart_item = get_object_or_404(Cart, customer = customer,product = product_id)
        item_exist = True
        


    except Exception as e:
         
        item_exist = False
         


    context = {
        'product': product,
        'item_exist': item_exist,
        'review_count': review_count,
        'already_reviewed': already_reviewed,
        'product_rating': product_rating,
        'rating_list': rating_list,
        'star_rating': star_rating,
        'questions': questions,
        'reviews': reviews
         
        
    }    
   
    return render(request, 'customer/product_detail.html', context )


def cart(request, current_view):

    if 'customer' in request.session:
        print('*********')
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
   
    return render(request, 'customer/cart.html')
    



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
    return redirect('customer:cart','list')


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
        order_details.order_status = 'order placed on ' + str(date.today())
        cart = Cart.objects.filter(customer = request.session['customer'])

        for item in cart:
            order_item = OrderItem(order_id = order_details.id, customer_id =  request.session['customer'], product_id = item.product.id, quantity = item.quantity, price = item.product.price )
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

        to_email = ['suvarna@cybersquare.org']

        
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

def product_review(request,id):
    purchased = OrderItem.objects.filter(product = id, customer = request.session['customer'] ).exists()
    if request.method == 'POST':
        customer = request.session['customer']
        title = request.POST['title']
        review = request.POST['customer_review']
        star_count = request.POST['star_count']

        customer_review = ProductReview(product_id = id, customer_id = customer,
                                         title = title, review = review, rating = star_count)
        customer_review.save()
        if request.FILES:
            for image in request.FILES.getlist('images'):
                 
                review_image = ReviewImage(review_id = customer_review.id, image = image)
                review_image.save()
        
        rating_list = get_rating(id)
        star_rating = get_star_rating(rating_list) 
        Product.objects.filter(id = id).update(rating = star_rating)
    return render(request, 'customer/product_review.html', {'purchased': purchased})

def myorders(request):
    orders = OrderItem.objects.filter(customer = request.session['customer'])
    print(orders)
    return render(request, 'customer/my_orders.html', {'orders': orders})


def profile(request):

    customer = Customer.objects.get(id = request.session['customer'])

    return render(request, 'customer/profile.html', {'customer': customer,})



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

            if request.GET.get('pid'):
                return redirect('customer:product_detail',request.GET.get('pid'))

            return redirect('customer:customer_home')
        else:
            message = 'Username or Password Incorrect'

    return render(request, 'customer/customer_login.html', {'message': message,})


def forgot_password_customer(request):
    return render(request, 'customer/forgot_password_customer.html')


def forgot_password_seller(request):
    return render(request, 'customer/forgot_password_seller.html')

def my_orders(request):
    
    orders = OrderItem.objects.filter(customer = request.session['customer'])
     
    return render(request, 'customer/my_orders.html', {'order_list': orders})

def cancel_order(requets):
    order_id = requets.POST['orderId']
    reason = requets.POST['reason']
    print(order_id, reason)
    try:
        order = OrderItem.objects.get(id = order_id)

        order.cancellation_reason = reason
        order.cancelled_date = date.today()
        order.status = 'cancelled'
        order.save()

    except Exception as e:
        print(e)
        pass

    return JsonResponse({'status': 200, 'message': 'Order Cancelled Succesfully'})
    
def add_product_qstn(request, product_id):

    if request.method == 'POST':
        question = request.POST['question']
        
        product_question = ProductQuestion(customer_id = request.session['customer'], 
                                           product_id = product_id, question = question)
        
        product_question.save()

        return redirect('customer:product_detail', product_id)
    return render(request, 'customer/post_questions.html',)


def display_qstn_details(request):
    qnstn_id = request.GET['qstnId']
    answer_set = Answers.objects.filter(question = qnstn_id)
     
    serialized_data = [{'id': answer.id, 'answer': answer.answer, 'customer': answer.customer.first_name} for answer in  answer_set]

    print(serialized_data)

    return JsonResponse({'data': serialized_data,})

def logout(request):
    del request.session['customer']
    request.session.flush()
    return redirect('customer:customer_home')


def update_customer_pofile(request):
    customer = Customer.objects.get(id = request.session['customer'])
    password_changed = False
    last_changed_date = ''

    if 'firstName' in request.POST:
        customer.first_name = request.POST['firstName']

    if 'lastName' in request.POST:
        customer.last_name = request.POST['lastName']

    if 'email' in request.POST:
            print('emaail')
            customer.email = request.POST['email']

    if 'mobile' in request.POST:
            print('emaail')
            customer.mobile = request.POST['mobile']

    if 'newPassword' in request.POST:
            
        customer.password = request.POST['newPassword']
        customer.is_password_changed = True
        customer.last_changed_on = date.today()
        last_changed_date = date.today()
        password_changed = True



    customer.save()
    return JsonResponse({'status': 200, })
