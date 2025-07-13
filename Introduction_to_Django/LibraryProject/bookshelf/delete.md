## delete

```bash
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()
print(book)
Book.objects.all()
```
