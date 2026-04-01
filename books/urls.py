"""URL routing for the books app."""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('book/<int:pk>/cart/add/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('book/<int:pk>/order/', views.book_order, name='book_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/default/', views.address_set_default, name='address_set_default'),
]