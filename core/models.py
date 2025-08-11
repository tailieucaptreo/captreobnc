from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from cloudinary.models import CloudinaryField
import unicodedata
import re


# ----- Danh mục chính -----
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name or "")


# ----- Hàm slug cho tên file -----
def slugify_filename(filename):
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\s-]', '', filename).strip().lower()
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename


# ----- Thư mục -----
class Folder(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subfolders')

    def __str__(self):
        return str(self.name or "")


# ----- Tài liệu -----
class Document(models.Model):
    title = models.CharField(max_length=255)
    file = CloudinaryField('file', resource_type="auto", folder="documents")  # lưu vào thư mục "documents"
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title or "")


# ----- Bài viết -----
class Post(models.Model):
    title = models.CharField(max_length=200)
    image = CloudinaryField('image', blank=True, null=True, folder="posts")
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title or "")

#capnhat