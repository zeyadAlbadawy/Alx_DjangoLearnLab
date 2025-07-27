"""
Permissions and Groups Setup:

Custom Permissions for Book model:

- can_view: View book list
- can_create: Add new books
- can_edit: Update existing books
- can_delete: Remove books

Groups:

- Viewers: can_view
- Editors: can_view, can_create, can_edit
- Admins: Full access

Enforced in views using @permission_required decorator.
"""
