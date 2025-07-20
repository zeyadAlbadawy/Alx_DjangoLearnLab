from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from .views import add_book, edit_book, delete_book
from . import views
from .views import list_books

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>', views.LibraryDetailView.as_view(), name = 'library_detail'),
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name = 'login_user'),
    path('logout_user/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout_user'),
    path('register/', views.register, name = 'register_user'),
    path('admin-view/', views.admin_view, name='admin_view'),
    path('librarian-view/', views.librarian_view, name='librarian_view'),
    path('member-view/', views.member_view, name='member_view'),
    path('add_book/', add_book, name='add_book'),
    path('edit_book/<int:pk>/', edit_book, name='edit_book'),
    path('delete_book/<int:pk>/', delete_book, name='delete_book'),
]