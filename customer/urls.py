from django.urls import path
from. import views

app_name = "customer"

urlpatterns = [   
   path('',views.customer_home, name='customer_home'),
   path('store',views.store,name='store'),
   path('product/detail/<int:product_id>',views.product_detail,name='product_detail'),
   path('cart/<str:current_view>',views.cart,name='cart'),
   path('placeOrder',views.place_order,name='place_order'),
   path('order/complete/<int:shipping_address>',views.update_payment,name='update_payment'),
   path('dashboard',views.dashboard,name='dasboard'),
   path('product/review/<int:id>',views.product_review,name='product_review'),
   path('profile/view',views.profile,name='profile'),
   path('product/question/post/<int:product_id>',views.add_product_qstn,name='add_product_qstn'),
   path('question/detail', views.display_qstn_details, name = "display_qstn_details"),
   path('seller/register',views.seller_register,name='seller_register'),
   path('seller/login',views.seller_login,name='seller_login'),
   path('customer/logout',views.logout,name='logout'),
   path('customer/update/profile',views.update_customer_pofile,name='update_customer_profile'),
   path('customer/order-item/cancel',views.cancel_order,name='cancel_order'),

   path('cart/item/remove/<int:cart_id>',views.remove_cart_item,name='remove_cart_item'),
   path('cart/item/update',views.update_cart,name='update_cart'),
   path('customer/order/history', views.my_orders, name = 'my_orders'),
   path('cart/review',views.review_cart,name='review_cart'),
   path('customer/products/order', views.order_product, name = 'order_product'),
   path('customer/signup',views.customer_signup,name='customer_signup'),
   path('customer/login',views.customer_login,name='customer_login'),
   path('forgotPassword/customer',views.forgot_password_customer,name='forgot_password_customer'),
   path('forgotPassword/seller',views.forgot_password_seller,name='forgot_password_seller'),
   

]