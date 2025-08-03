from rest_framework import serializers
from .models import Book

# This converts the data into Json
class BookSerializer (serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'