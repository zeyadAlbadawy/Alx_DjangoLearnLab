from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import BookSerializer
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Book, Author
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

# Create your views here.
class BookCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('title', 'publication_year' ,'author')
    search_fields = ['title']

    
# Retrieve
class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Update
class BookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


# Delete
class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    # def get_permissions(self):
    #     if self.req.method == 'GET':
    #         return [permissions.AllowAny()]
    #     return [permissions.IsAuthenticated()]