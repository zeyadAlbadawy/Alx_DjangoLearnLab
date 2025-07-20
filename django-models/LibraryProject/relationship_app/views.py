from django.shortcuts import render, redirect
from .models import Book
from .models import Library
from django.views.generic.detail import DetailView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import  user_passes_test



# ROLES

def check_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Admin'

def check_librarian(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Librarian'

def check_member(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Member'

@user_passes_test(check_admin)
def admin_view(request):
    return render(request, 'admin_view.html')

@user_passes_test(check_librarian)
def librarian_view(request):
    return render(request, 'librarian_view.html')

@user_passes_test(check_member)
def member_view(request):
    return render(request, 'member_view.html')

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




