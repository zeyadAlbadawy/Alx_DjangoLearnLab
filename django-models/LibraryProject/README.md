## Simple Django Application

### Start a New Project

```bash
python -m django startproject LibraryProject
```

### Run the Development Server

```bash
python manage.py runserver
```

### Generate New App

```bash
 python manage.py startapp bookshelf.
```

### Migrating and Running Django App

```bash
python manage.py makemigrations
python manage.py migrate
```

## Django Admin Integration

- Registered the `Book` model with the admin interface.
- Customized list display to show `title`, `author`, and `publication_year`.
- Enabled filtering by publication year.
- Added search capability for `title` and `author`.
