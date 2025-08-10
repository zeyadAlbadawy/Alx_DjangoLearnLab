from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import BookSerializer
from .models import Book, Author

# Create your views here.
class BookListView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Retrieve
class BookCreateView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Update
class BookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Delete
class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


# class BookListCreateView(generics.CreateAPIView):
#     queryset = Book.objects.all()
#     serializer_class=BookSerializer

#     # all the users can view the books but authenticated only can create
#     def get_permissions(self):
#         if self.req.method == 'GET':
#             return [permissions.AllowAny()]
#         return [permissions.IsAuthenticated()]
    

# class UpdateAndDeleteBookListView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class= BookSerializer

#     def get_permissions(self):
#         if self.req.method == 'GET':
#             return [permissions.AllowAny()]
#         return [permissions.IsAuthenticated()]

