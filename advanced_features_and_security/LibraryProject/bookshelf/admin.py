from django.contrib import admin
from .models import Book
from .models import CustomUser
from .models import CustomUserManager
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year' )
    list_filter = ('publication_year',)
    search_fields = ('title', 'author')

class CustomUserAdmin(UserAdmin): 
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('date_of_birth', 'profile_photo')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets +  (
        ('Additional Info', {'fields': ('date_of_birth', 'profile_photo')}),
    )
    list_display = ['username', 'email', 'date_of_birth', 'is_staff']
admin.site.register( Book, BookAdmin)
admin.site.register(CustomUser, CustomUserAdmin)