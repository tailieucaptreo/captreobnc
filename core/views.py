import unicodedata
import re
import cloudinary.uploader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import Document, Category, Folder, Post
from .forms import PostForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import cloudinary.utils



# ======= Helper function =======
def slugify_filename(filename):
    """Chuyển tên file thành dạng an toàn (ASCII, không ký tự đặc biệt)."""
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


# ======= Trang chủ =======
def home(request):
    categories = Category.objects.all()
    documents = Document.objects.all().order_by('-uploaded_at')
    posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'home.html', {
        'categories': categories,
        'documents': documents,
        'posts': posts,
    })


# ======= Danh mục & Thư mục =======
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    folders = Folder.objects.filter(category=category)
    return render(request, 'category_detail.html', {
        'category': category,
        'folders': folders,
    })


def folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    documents = Document.objects.filter(folder=folder)
    return render(request, 'folder_detail.html', {
        'folder': folder,
        'documents': documents,
    })


def documents_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    documents = Document.objects.filter(folder__category=category).order_by('-uploaded_at')
    return render(request, 'documents_by_category.html', {
        'documents': documents,
        'category': category,
    })


# ======= Upload tài liệu =======
@login_required
def upload_document(request):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        files = request.FILES.getlist('files')
        folder_id = request.POST.get('folder')
        folder = Folder.objects.get(id=folder_id) if folder_id else None

        for f in files:
            safe_name = slugify_filename(f.name)

            # Upload file lên Cloudinary (resource_type="raw" cho mọi loại file)
            upload_result = cloudinary.uploader.upload(
                f,
                folder="documents/",
                resource_type="raw",
                public_id=safe_name.split(".")[0]
            )

            # Lưu vào DB
            Document.objects.create(
                title=safe_name,
                file_url=upload_result["secure_url"],
                folder=folder,
                uploaded_by=request.user
            )

        messages.success(request, "Tài liệu đã được tải lên thành công.")
        return redirect('home')

    folders = Folder.objects.all()
    return render(request, 'upload.html', {'folders': folders})


# ======= Download tài liệu từ Cloudinary =======
@login_required
def download_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return redirect(doc.file_url)  # dùng file_url thay vì file.url


# ======= Xem tài liệu =======
@login_required
def view_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return render(request, 'view_document.html', {'document': doc})


# ======= Xóa tài liệu =======
@login_required
def delete_document(request, doc_id):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    document = get_object_or_404(Document, id=doc_id)

    # Xóa file trên Cloudinary
    public_id = document.title.rsplit(".", 1)[0]  # bỏ phần đuôi .pdf/.docx
    cloudinary.uploader.destroy(f"documents/{public_id}", resource_type="raw")

    document.delete()
    messages.success(request, "Tài liệu đã được xoá.")
    return redirect('home')


# ======= Quản lý Danh mục & Thư mục =======
@login_required
def create_category(request):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        name = request.POST['name']
        Category.objects.create(name=name)
        messages.success(request, "Danh mục đã được tạo.")
        return redirect('home')

    return render(request, 'create_category.html')


@login_required
def delete_category(request, cat_id):
    if request.user.is_staff:
        Category.objects.filter(id=cat_id).delete()
        messages.success(request, "Danh mục đã được xoá.")
    return redirect('home')


@login_required
def create_folder(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        name = request.POST['name']
        Folder.objects.create(name=name, category=category)
        messages.success(request, "Thư mục đã được tạo.")
        return redirect('category_detail', category_id=category.id)

    return render(request, 'create_folder.html', {'category': category})


# ======= Xóa thư mục =======
@login_required
def delete_folder(request, folder_id):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    folder = get_object_or_404(Folder, id=folder_id)

    # Xóa tất cả tài liệu trong thư mục (Cloudinary + DB)
    for doc in Document.objects.filter(folder=folder):
        public_id = doc.title.rsplit(".", 1)[0]
        cloudinary.uploader.destroy(f"documents/{public_id}", resource_type="raw")
        doc.delete()

    folder.delete()
    messages.success(request, "Thư mục đã được xoá.")
    return redirect('category_detail', category_id=folder.category.id)


# ======= Bài viết =======
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'post_list.html', {'posts': posts})


@login_required
def create_post(request):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Bài viết đã được đăng.")
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        if post.image:
            post.image.delete()
        post.delete()
        messages.success(request, "Bài viết đã bị xoá.")
        return redirect('post_list')

    return render(request, 'confirm_delete.html', {'post': post})


# ======= Tìm kiếm =======
def search_documents(request):
    query = request.GET.get('q')
    documents = Document.objects.filter(
        Q(title__icontains=query) |
        Q(uploaded_by__username__icontains=query) |
        Q(folder__name__icontains=query)
    ) if query else []
    return render(request, 'search_results.html', {
        'documents': documents,
        'query': query
    })


def api_search_documents(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        documents = Document.objects.filter(title__icontains=query)[:10]
        results = [
            {
                'id': doc.id,
                'title': doc.title,
                'download_url': f'/download/{doc.id}/'
            } for doc in documents
        ]
    return JsonResponse(results, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # chỉ user login mới vào được
def get_signed_download(request, public_id):
    url, options = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type="raw",   # PDF, DOC, RAR... phải là raw
        type="upload",
        sign_url=True
    )
    return Response({"download_url": url})
