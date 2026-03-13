import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_request_system.settings')
django.setup()

from django.contrib.auth.models import User
from access_requests.models import System

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superuser 'admin' created.")
else:
    print("Superuser 'admin' already exists.")

systems = [  
    ('SAP / ERP System', 'Enterprise Resource Planning'),
    ('VPN Access', 'Remote Access'),
    ('Salesforce CRM', 'Customer Relationship Management'),
    ('File Server (Z: Drive)', 'Shared File Storage'),
    ('HR Management Portal', 'Human Resources'),
    ('Special Internet Access', 'Unrestricted Internet'),
    ('Corporate Email', 'Email Account'),
    ('Adobe Creative Cloud', 'Design Software License'),
]

for name, desc in systems:
    if not System.objects.filter(name=name).exists():
        System.objects.create(name=name, description=desc)
        print(f"System '{name}' created.")
    else:
        print(f"System '{name}' already exists.")
