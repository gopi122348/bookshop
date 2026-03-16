from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from books import views as book_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('books.urls')),

    path(
        'accounts/login/',
        auth_views.LoginView.as_view(),
        name='login'
    ),

    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='book_list'),
        name='logout'
    ),

    path(
        'accounts/register/',
        book_views.register,
        name='register'
    ),
]