from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import BookSerializer
from .models import Book, Author

# Create your views here.
class BookListCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class=BookSerializer

    # all the users can view the books but authenticated only can create
    def get_permissions(self):
        if self.req.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    

class UpdateAndDeleteBookListView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class= BookSerializer

    def get_permissions(self):
        if self.req.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

