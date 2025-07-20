from django.shortcuts import render
from .models import Book, Library
from django.views.generic import DetailView
 
# Create your views here.
def List_books(request):
    books = Book.objects.select_related('author').all()
    context = {'books': books}
    return render(request, 'relationship_app/list_books.html', context)

