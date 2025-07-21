from django.contrib import admin
from .models import Category, Folder, Document, Post

admin.site.register(Category)
admin.site.register(Folder)
admin.site.register(Document)
admin.site.register(Post)
