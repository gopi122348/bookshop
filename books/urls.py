from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Book CRUD
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('book/<int:pk>/cart/add/', views.cart_add, name='cart_add'),
    # Orders
    path('book/<int:pk>/order/', views.book_order, name='book_order'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Comment these out until views are ready
    # path('order/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    # path('cart/', views.cart_view, name='cart_view'),
    # path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    # path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),
    # path('orders/', views.order_history, name='order_history'),
]