from django.shortcuts import render, redirect
from .models import Book
from .models import Library
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if(form.is_valid):
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        context = {'from': form}
        return render(request, 'relationship_app/login.html', context) 


def user_logout(request):
    logout(request)
    return render(request, 'relationship_app/logout.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if(form.is_valid):
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
        context =  {'form': form}
        return render(request, 'relationship_app/register.html', context)


# Create your views here.
def list_books(request):
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'relationship_app/list_books.html', context)

class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'