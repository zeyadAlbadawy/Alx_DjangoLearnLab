from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from .forms import ExampleForm
from .models import Book
# Create your views here.
def index(request): 
    return HttpResponse("Welcome to my Book Shelf!.")



@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

@permission_required('bookshelf.can_create', raise_exception=True)
def create_book(request):
    # implement book creation form logic
    ...

@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    # implement edit form logic
    ...

@permission_required('relationship_app.can_delete', raise_exception=True)
def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    # redirect to list
