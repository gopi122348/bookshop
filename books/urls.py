from django.urls import path
from . import views


urlpatterns = [
    # Main pages
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Cart URLs
    path('book/<int:pk>/cart/add/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),

    # Order URLs
    path('book/<int:pk>/order/', views.book_order, name='book_order'),
    path('orders/', views.order_history, name='order_history'),
]