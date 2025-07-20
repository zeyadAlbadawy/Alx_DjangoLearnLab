from relationship_app.models import *

# 1. Query all books by a specific author
book_by_author = Book.objects.filter(author_name = 'John Doe')
print([book.title for book in book_by_autor ])


# 2. List all books in a library
library = Library.objects.get(name="Central Library")
print([book.title for book in library.books.all()])


# 3. Retrieve the librarian for a library
librarian = library.objects.get(library=library)
print(librarian.name)