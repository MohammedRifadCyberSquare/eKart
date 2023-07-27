from django.shortcuts import render,redirect
from .models import EkartAdmin,Category
# Create your views here.

def admin_login(request):
    message = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            admin = EkartAdmin.objects.get(user_name = username, password = password)
            return redirect('ekart_admin:admin_home')
        except Exception as e:
            print(e)
            message = 'Invalid Username Or Password'


    return render(request,'ekart_admin/admin_login.html', {'message': message,})

def admin_home(request):
    return render(request,'ekart_admin/admin_home.html')

def view_category(request):
    category_list = Category.objects.all()
    print(category_list)

    return render(request,'ekart_admin/view_category.html', {'category': category_list})

def add_category(request):
    message = ''
    if request.method == 'POST':
        category = request.POST['category_name'].lower()
        description = request.POST['description']
        cover_pic = request.FILES['cover_pic']

        category_exist = Category.objects.filter(category = category).exists()

        if not category_exist:
            category = Category(category = category, description = description, cover_pic = cover_pic)
            category.save()
            message = 'Category Added'
        else:
            message = 'Already Added'
    return render(request,'ekart_admin/add_category.html', {'message': message})

def pending_sellers(request):
    return render(request,'ekart_admin/pending_sellers.html')

def approved_sellers(request):
    return render(request,'ekart_admin/approved_sellers.html')

def customers(request):
    return render(request,'ekart_admin/customers.html')