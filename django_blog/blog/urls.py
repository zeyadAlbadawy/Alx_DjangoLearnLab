from django.urls import path
from .views import UserLoginView, UserLogoutView, register, profile
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='blog/home.html'), name='home'),

    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),


        # Comments
    path("post/<int:pk>/comments/new/", views.CommentCreateView.as_view(), name="comment-create"),
    path("comment/<int:pk>/update/", views.CommentUpdateView.as_view(), name="comment-update"),
    path("comment/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment-delete"),


    path('search/', views.search_posts, name='search_posts'),
    path('tags/<str:tag_name>/', views.posts_by_tag, name='posts_by_tag'),
    path("tags/<slug:tag_slug>/", views.PostByTagListView.as_view(), name="posts_by_tag"),

]
