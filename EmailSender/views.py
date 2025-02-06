from django.views import View
from django.http import JsonResponse
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To
import concurrent.futures
from datetime import datetime, timedelta
from django.db import connection, OperationalError

class SendEmailView(View):
    def __init__(self):
        self.day_limit = settings.EMAIL_SEND_DAYS_LIMIT
        self.start_date = settings.START_DATE


    def fetch_emails(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM tbl_users;")
                emails = [row[0] for row in cursor.fetchall()]
                print("emails:",emails)
                if not emails:
                    return None  # No active users found
            return emails
        except OperationalError as e:
            print(f"Database error: {e}")
            return None


    def send_email(self, to_email):
        """
        Sends an email to a single recipient.
        :param to_email: Email address of the recipient.
        """
        subject = settings.EMAIL_SUBJECT
        plain_text_content = settings.EMAIL_MESSAGE

        message = Mail(
            from_email=From(settings.DEFAULT_FROM_EMAIL),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=plain_text_content,
        )
        
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            print(f"Email sent to {to_email} - Status: {response.status_code}")
        except Exception as e:
            print(f"Error sending to {to_email}: {e}")

    def get(self, request, *args, **kwargs):
        # Check if the day limit has been reached
        current_date = datetime.now()
        if (current_date - self.start_date).days >= self.day_limit:
            return JsonResponse({"status": "Email sending limit reached"})

        # Fetch emails from the database
        recipient_list = self.fetch_emails()

        if not recipient_list:
            return JsonResponse({"status": "No active users found to send emails"})

        # Send emails in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            executor.map(self.send_email, recipient_list)

        return JsonResponse({"status": f"Emails sent successfully to {len(recipient_list)} users"})
