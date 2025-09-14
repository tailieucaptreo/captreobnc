from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from .views import get_signed_download

def google_login(request):
    return redirect('social:begin', backend='google-oauth2')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ✅ CHỈ CẦN 1 LẦN
    path('oauth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('login/', google_login, name='login'),  # ✅ Thay vì LoginView
    path('ckeditor/', include('ckeditor_uploader.urls')),  # ✅ CKEditor upload
     path("download/<path:public_id>/", get_signed_download, name="get_signed_download"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
