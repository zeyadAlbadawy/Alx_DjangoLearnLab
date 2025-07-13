---

#### 🔵 `retrieve.md`

````markdown
# Retrieve Book Instance

```python
from bookshelf.models import Book
book = Book.objects.get(title="1984")
print(book.title, book.author, book.publication_year)
# 1984 George Orwell 1949
```
````
