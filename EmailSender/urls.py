from django.urls import path
from .views import SendEmailView, SendFailureEmail, SendSuccessEmail
from dotenv import load_dotenv
load_dotenv()
import os 

urlpatterns = [
    path(f'{os.getenv("SEND_EMAIL")}', SendEmailView.as_view(), name='send-email'),
    path(f'{os.getenv("SEND_EMAIL")}'+f'{os.getenv("SUCCESS_EMAIL")}',SendSuccessEmail.as_view(),name='success-email'),
    path(f'{os.getenv("SEND_EMAIL")}'+f'{os.getenv("FAILURE_EMAIL")}',SendFailureEmail.as_view(),name='failure-email')
]