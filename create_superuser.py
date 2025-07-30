import os
import django

print("Running create_superuser.py...")  # ✅ In ra đầu tiên để kiểm tra script có chạy

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tailieucaptreo.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = "captreobnc01"
email = "captreobnc01@gmail.com"
password = "Captreo2025#"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser created successfully.")
else:
    print("ℹ️ Superuser already exists.")
