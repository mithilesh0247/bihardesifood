from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('', views.home, name='home'),

    #Cart Operation Route 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/ajax/increase/<int:product_id>/', views.ajax_increase_quantity, name='ajax_increase_quantity'),
    path('cart/ajax/decrease/<int:product_id>/', views.ajax_decrease_quantity, name='ajax_decrease_quantity'),
    path('cart/ajax/remove/<int:product_id>/', views.ajax_remove_from_cart, name='ajax_remove_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    #Admin See How orders is there 
    path('admin-orders/', views.order_list, name='order_list'),
    #UserAuthentication Process 
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # ✅ My Orders (if you want customer order history)
    path('my-orders/', views.my_orders, name='my_orders'),

    
]
