from django.urls import path, include
from . import views
from .views import list_books

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>', views.LibraryDetailView.as_view(), name = 'library_detail'),
    path('login,', views.user_login, name = 'login_user'),
    path('logout_user/', views.user_logout, name='logout_user'),
    path('register/', views.register, name = 'register_user')
]