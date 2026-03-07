# bookshop/urls.py
# Root URL configuration — wires admin and books app
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
path('admin/', admin.site.urls),
path('', include('books.urls')),
]