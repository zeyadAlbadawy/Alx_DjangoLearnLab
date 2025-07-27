from relationship_app.models import Book, Library, Librarian, Author

# Query all books by a specific author
author_name = "John Doe"
author = Author.objects.get(name=author_name)
books_by_author = Book.objects.filter(author=author)

# List all books in a library
library_name = "Central Library"
library = Library.objects.get(name=library_name)
print(f"Books in {library.name}:")
for book in library.books.all():
    print(book.title)

# Retrieve the librarian for a library
librarian = Librarian.objects.get(library=library)
print(f"Librarian of {library.name} is {librarian.name}")
