import os
import django
from django.conf import settings
from django.core.mail import send_mail

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_request_system.settings')
django.setup()

def test_email():
    print(f"Testing email settings...")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    
    try:
        # Note: Using settings.EMAIL_HOST_USER as sender to ensure it matches auth
        send_mail(
            subject='Test Email from Access Request System',
            message='This is a test email to verify SMTP settings.',
            from_email=settings.EMAIL_HOST_USER, 
            recipient_list=['nattchai_u@thonglorpet.com'],
            fail_silently=False
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print("\n--- ERROR DETAILS ---")
        print(e)
        print("---------------------")

if __name__ == "__main__":
    test_email()
