from django.shortcuts import render,redirect
from .models import EkartAdmin
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
    return render(request,'ekart_admin/view_category.html')

def add_category(request):
    if request.method == 'POST':
        category = request.POST['category']
        description = request.POST['description']
        cover_pic = request.FILES['cover_pic']

        category
    return render(request,'ekart_admin/add_category.html')

def pending_sellers(request):
    return render(request,'ekart_admin/pending_sellers.html')

def approved_sellers(request):
    return render(request,'ekart_admin/approved_sellers.html')

def customers(request):
    return render(request,'ekart_admin/customers.html')