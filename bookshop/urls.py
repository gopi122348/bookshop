#Root URL config - adds auth URLs alongside admin and books

from django.contrib import admin

from django.urls import path, include

from django.contrib.auth import views as auth views

from books import views as book views

urlpatterns = [

    path ('admin/', admin.site.urls),

    path(", include('books.urls')),

# Built-in login/logout (Django provides the logic) 
    path('accounts/login/',

        auth_views.LoginView.as_view()

        , name='login'),

    path('accounts/logout/',

    auth_views.LogoutView.as_view(next_page='book_list')

    , name='logout'),

# Custom registration view (defined in books/views.py) 
    path('accounts/register/',

        book_views.register, name='register'),
]