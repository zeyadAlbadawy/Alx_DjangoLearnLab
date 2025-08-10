## API Endpoints

- GET /books/ → List all books (public)
- POST /books/ → Create book (auth only)
- GET /books/<id>/ → Retrieve book (public)
- PUT /books/<id>/ → Update book (auth only)
- DELETE /books/<id>/ → Delete book (auth only)

Permissions:

- Authenticated users can modify data.
- Unauthenticated users can only read data.
