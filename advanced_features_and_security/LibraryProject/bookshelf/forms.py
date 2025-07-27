from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date']

class BookSearchForms(forms.Form):
    query = forms.CharField(
        max_length= 100
        required=False
        label='Search For A book'
        widget=forms.TextInput(attrs={'placeholder': 'Enter Title'})
    )

    class ExampleForm(forms.Form):
        name = forms.CharField(max_length=100, required=True)
        email = forms.EmailField(required=True)
        message = forms.CharField(widget=forms.Textarea, required=True)
