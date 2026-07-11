import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

@receiver(post_migrate)
def create_superuser_post_migrate(sender, **kwargs):
    # 'api' app-এর মাইগ্রেশন রান হওয়া শেষ হলে এই হুকটি কাজ করবে
    if sender.name == 'api':
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        reset_password = os.environ.get('RESET_SUPERUSER_PASSWORD', '').lower() in {
            '1', 'true', 'yes', 'on'
        }

        if not username or not password:
            print("Superuser environment variables are missing. Skipping admin creation.")
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f'Superuser "{username}" created successfully via post_migrate signal.')
        elif reset_password:
            user.email = email
            user.set_password(password)
            user.save(update_fields=['email', 'password'])
            print(f'Superuser "{username}" password rotated successfully via post_migrate signal.')
        else:
            print(f'Superuser "{username}" already exists; password was not changed.')
