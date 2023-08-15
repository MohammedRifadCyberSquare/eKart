from django.urls import path
from. import views

app_name = "Seller"

urlpatterns = [   
    path('',views.seller_home,name="seller_home"),
    path('product/add',views.add_product,name="add_product"),
    # path('add_category',views.add_category,name="add_category"),
    path('product',views.view_products,name="view_product"),
    # path('view_category',views.view_category,name="view_category"),
    path('profile',views.profile,name="profile"),
    path('password/change',views.change_password,name="change_password"),
    path('product/reviews/<int:product_id>',views.product_reviews,name="product_reviews"),
    path('product/questions/<int:product_id>',views.product_questions,name="product_questions"),

    path('myOrders',views.view_orders,name="view_orders"),
    path('stock/update',views.update_stock,name="update_stock"),
    path('get/stock/detail',views.get_stock_details,name="get_stock_details"),
    path('recent/orders',views.recent_orders,name="recent_orders"),
    path('order/items/<str:order_no>',views.order_items,name="order_items"),
    path('order/item/status/update/<int:order_id>', views.update_order_status, name = "update_order_status" ),
    path('order/history',views.order_history,name="order_history"),

   
]