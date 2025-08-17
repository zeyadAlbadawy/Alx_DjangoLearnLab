from django.urls import path
from .views import UserLoginView, UserLogoutView, register, profile
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='blog/home.html'), name='home'),

    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
]
