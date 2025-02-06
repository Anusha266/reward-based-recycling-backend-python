# tasks.py
from celery import shared_task
from django.conf import settings
from datetime import datetime, timedelta
from .views import SendEmailView

@shared_task
def send_scheduled_emails():
    view = SendEmailView()
    
    current_date = datetime.now()
    print("Checking date difference...")
    if (current_date - view.start_date).days < settings.EMAIL_SEND_DAYS_LIMIT:
        print("Condition met, calling view.get(None)")
        view.get(None)
    else:
        print("Condition not met")