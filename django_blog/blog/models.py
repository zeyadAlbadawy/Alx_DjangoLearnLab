from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    tags = TaggableManager()   # replaces the custom Tag model

    def __str__(self):
        return self.title

def user_avatar_upload_path(instance, filename):
    return f'avatars/user_{instance.user_id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=user_avatar_upload_path, blank=True, null=True)

    def __str__(self):
        return f"Profile({self.user.username})"

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

