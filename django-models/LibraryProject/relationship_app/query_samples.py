from relationship_app.models import Book, Library, Librarian

# Query all books by a specific author
author_name = 'John Doe'
books_by_author = Book.objects.filter(name=author_name)
print("Books by John Doe:")
for book in books_by_author:
    print(book.title)

# List all books in a library
library_name = "Central Library"
library = Library.objects.get(name=library_name)
print(f"Books in {library.name}:")
for book in library.books.all():
    print(book.title)

# Retrieve the librarian for a library
librarian = Librarian.objects.get(library=library)
print(f"Librarian of {library.name} is {librarian.name}")
