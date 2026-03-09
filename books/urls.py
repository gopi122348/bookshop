# books/urls.py
# URL patterns mapping paths to CRUD views

from django.urls import path
from . import views


urlpatterns = [
    path('checkout/',views.checkout,name='checkout'),
    path('order/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    path('cart/',views.cart_view,   name='cart_view'),
    path('cart/add/<int:pk>/', views.cart_add,    name='cart_add'),
    path('cart/remove/<int:pk>/',views.cart_remove, name='cart_remove'),
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('orders/', views.order_history, name='order_history'),

]