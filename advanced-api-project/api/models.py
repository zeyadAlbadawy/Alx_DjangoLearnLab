from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class Author(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Book(models.Model):
    title=models.CharField(max_length=300)
    publication_year= models.PositiveIntegerField()
    author = models.ForeignKey(Author, related_name='books' ,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.title} ({self.publication_year})"
    



