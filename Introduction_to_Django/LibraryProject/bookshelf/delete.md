## delete

```bash
book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()
print(Book.objects.all())
```
