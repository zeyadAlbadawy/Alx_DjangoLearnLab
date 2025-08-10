from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import BookSerializer
from .models import Book, Author
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

# Create your views here.
class BookCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.req.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
# Retrieve
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Update
class BookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.req.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]



# Delete
class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.req.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]




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

