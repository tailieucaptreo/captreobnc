from django import forms
from .models import Category, Folder, Document, Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'category']


# Form này chỉ dùng nếu upload 1 file/lần
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'folder']


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = ['file_url', 'folder']
