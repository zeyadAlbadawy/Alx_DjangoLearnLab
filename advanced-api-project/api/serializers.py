from rest_framework import serializers
from .models import Book, Author
import datetime


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
    def checkPublicationYear(self, value):
        current_year = datetime.date.today().year
        if(value > current_year):
            raise serializers.ValidationError('Publication year can not be in the future!')
        return value



class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    class Meta:
        model = Author
        fields = ['id', 'name', 'book']