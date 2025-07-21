from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse
from django.db.models import Q
from django.contrib import messages
from .models import Document, Category, Folder, Post
from .forms import PostForm
from django.http import JsonResponse

def home(request):
    categories = Category.objects.all()
    documents = Document.objects.all().order_by('-uploaded_at')
    posts = Post.objects.all().order_by('-created_at')[:5]  # lấy 5 bài viết mới nhất

    return render(request, 'home.html', {
        'categories': categories,
        'documents': documents,
        'posts': posts,
    })

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

@login_required
def upload_document(request):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        files = request.FILES.getlist('files')  # lấy danh sách file
        folder_id = request.POST.get('folder')
        folder = Folder.objects.get(id=folder_id) if folder_id else None

        for f in files:
            Document.objects.create(
                title=f.name,  # dùng tên file làm tiêu đề
                file=f,
                folder=folder,
                uploaded_by=request.user
            )
        return redirect('home')

    folders = Folder.objects.all()
    return render(request, 'upload.html', {'folders': folders})


@login_required
def download_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return FileResponse(doc.file.open(), as_attachment=True)

@login_required
def view_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return render(request, 'view_document.html', {'document': doc})

@login_required
def delete_document(request, doc_id):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    document = get_object_or_404(Document, id=doc_id)
    if document.file:
        document.file.delete()
    document.delete()
    return redirect('home')

@login_required
def create_category(request):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')

    if request.method == 'POST':
        name = request.POST['name']
        Category.objects.create(name=name)
        return redirect('home')
    
    return render(request, 'create_category.html')

@login_required
def delete_category(request, cat_id):
    if request.user.is_staff:
        Category.objects.filter(id=cat_id).delete()
    return redirect('home')

@login_required
def create_folder(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if not request.user.is_staff:
        return render(request, 'no_permission.html')
    
    if request.method == 'POST':
        name = request.POST['name']
        Folder.objects.create(name=name, category=category)
        return redirect('category_detail', category_id=category.id)
    
    return render(request, 'create_folder.html', {'category': category})

@login_required
def delete_folder(request, folder_id):
    if not request.user.is_staff:
        return render(request, 'no_permission.html')
    
    folder = get_object_or_404(Folder, id=folder_id)
    Document.objects.filter(folder=folder).delete()
    folder.delete()
    messages.success(request, "Thư mục đã được xoá.")
    return redirect('category_detail', category_id=folder.category.id)

# ------- BÀI VIẾT --------

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