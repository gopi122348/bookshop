from django.urls import path
from . import views

urlpatterns = [
    # ... your existing urls ...
    path('book/<int:pk>/cart/add/', views.cart_add, name='cart_add'),
    path('book/<int:pk>/order/', views.book_order, name='book_order'),
    
    # Uncomment these:
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    path('orders/', views.order_history, name='order_history'),
]