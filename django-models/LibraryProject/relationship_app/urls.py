from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from . import views
from .views import list_books

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>', views.LibraryDetailView.as_view(), name = 'library_detail'),
    path('login,', LoginView.as_view(template_name='relationship_app/login.html'), name = 'login_user'),
    path('logout_user/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout_user'),
    path('register/', views.register, name = 'register_user')
]