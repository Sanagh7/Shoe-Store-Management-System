from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import your views

urlpatterns = [
    path('', views.home, name='home'),
    path('shoes/', views.shoe_list, name='shoe_list'), 
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:shoe_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('shoe/<int:shoe_id>/', views.shoe_detail, name='shoe_detail'),
    path('sports-shoe/', views.sports_shoe, name='sports_shoe'),
    path('add-shoe/', views.add_shoe, name='add_shoe'),
    path('category/<int:category_id>/', views.category_view, name='category_view'),
    path('billing/', views.billing_view, name='billing'),
    path('services/', views.services, name='services'),
    path('thankyou/', views.thankyou_view, name='thankyou'),
    path('register/', views.register_view, name='register'),
    path('check-login-and-proceed/', views.check_login_and_proceed, name='check_login_and_proceed'),
]
