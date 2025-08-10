from django.contrib import admin
from django.urls import path, include
from .views import BookListCreateView, UpdateAndDeleteBookListView
urlpatterns = [
    path('books/', BookListCreateView.as_view, name='book-list'),
    path('books/<int:pk>/', BookListCreateView.as_view, name='book-one')
]
