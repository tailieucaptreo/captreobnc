from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()

# Lưu lại admin
admins = list(User.objects.filter(is_superuser=True).values())

# Xóa toàn bộ dữ liệu trong tất cả model trừ auth_user và quyền
for model in apps.get_models():
    if model._meta.db_table not in [
        'auth_user', 'auth_group', 'auth_permission', 'django_content_type',
        'auth_user_groups', 'auth_user_user_permissions'
    ]:
        model.objects.all().delete()

# Khôi phục admin nếu bị mất (phòng trường hợp nhầm)
for admin_data in admins:
    User.objects.update_or_create(
        username=admin_data['username'],
        defaults=admin_data
    )

print("✅ Reset DB thành công, tài khoản admin vẫn giữ nguyên!")
