"""
Django settings for Reward_Based_Recycling_Tracker project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from celery.schedules import crontab
from datetime import datetime
load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY',default='')

# Use environment variables for email and message content
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', default='')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', default='')

# Email subject and message can also be placed here for flexibility
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT', default='Recycling Reminder')

EMAIL_MESSAGE = os.getenv('EMAIL_MESSAGE', default='''
Hi there! 🌱

We hope this message finds you well. 😊

This is a friendly reminder to continue your amazing efforts in recycling. Your contribution is making a huge difference in creating a more sustainable future for all of us! 🌍

Remember:
- Recycling helps reduce waste and protects our environment.
- Small actions like separating recyclables from trash can make a big impact.
- Together, we can create a cleaner, greener world for future generations. 🌿

We believe in you and your efforts to make the world a better place. Keep up the great work!

Best regards,  
The Recycling Team 🌎

P.S. If you ever need more information or have any questions, don't hesitate to reach out. We're always here to help you on your recycling journey! 📩

Thank you for being a champion of change! 💚
''')

EMAIL_SEND_DAYS_LIMIT = int(os.getenv('EMAIL_SEND_DAYS_LIMIT', default=7))  # Default to 7 days
MAX_WORKERS=int(os.getenv('MAX_WORKERS'),3)

start_date_str = os.getenv('START_DATE')  # Fetch from .env

# Parse the string to a datetime object
START_DATE = datetime.strptime(start_date_str, '%Y-%m-%d')
DJANGO_SETTINGS_MODULE=os.getenv('DJANGO_SETTINGS_MODULE')

DEBUG = False

ALLOWED_HOSTS = ["reward-based-recycling-backend-python-anusha2669452-yir05l8u.leapcell.dev",
                 "127.0.0.1",
                 "reward-based-recycling-backend-python-1.onrender.com"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'EmailSender',
    'backend_services',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Reward_Based_Recycling_Tracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Reward_Based_Recycling_Tracker.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Uses local Redis if not set
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# settings.py
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULE = {
    'send-emails-everyday': {
        'task': 'EmailSender.tasks.send_scheduled_emails',
        'schedule': crontab(hour=0, minute=29),  
    },
    'send-emails-everynight': {
        'task': 'EmailSender.tasks.send_scheduled_emails',
        'schedule': crontab(hour=0, minute=30),  
    },
}