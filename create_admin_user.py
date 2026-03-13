import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_request_system.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
password = 'password1234'
email = 'admin@example.com'

try:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created successfully.")
        print(f"Password: {password}")
    else:
        print(f"Superuser '{username}' already exists.")
except Exception as e:
    print(f"Error creating superuser: {e}")
