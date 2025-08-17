from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

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

