from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload'),
    path('download/<int:doc_id>/', views.download_document, name='download'),

    path('create_category/', views.create_category, name='create_category'),
    path('delete_category/<int:cat_id>/', views.delete_category, name='delete_category'),

    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('category/<int:category_id>/create_folder/', views.create_folder, name='create_folder'),
    path('folder/<int:folder_id>/', views.folder_detail, name='folder_detail'),

    path('posts/', views.post_list, name='post_list'),
    path('create_post/', views.create_post, name='create_post'),

    path('search/', views.search_documents, name='search'),

    path('documents/category/<int:category_id>/', views.documents_by_category, name='documents_by_category'),

    path('category/<int:category_id>/folder/create/', views.create_folder, name='create_folder'),

    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),

    path('document/<int:doc_id>/delete/', views.delete_document, name='delete_document'),

    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    path('api/search/', views.api_search_documents, name='api_search'),

    path('view/<int:doc_id>/', views.view_document, name='view_document'),
]
