from django.views import View
from django.http import JsonResponse
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To
import concurrent.futures
from datetime import datetime
from django.db import connection, OperationalError
import json
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To
import concurrent.futures
from datetime import datetime
from django.db import connection, OperationalError
from rest_framework import status  # Import Django REST framework status codes

class SendEmailView(View):
    def __init__(self):
        self.day_limit = settings.EMAIL_SEND_DAYS_LIMIT
        self.start_date = settings.START_DATE

    def fetch_emails(self):
        """Fetch user emails from the database."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT email FROM tbl_users;")
                emails = [row[0] for row in cursor.fetchall()]
                return emails if emails else None  # Return None if no emails found
        except OperationalError:
            return {"error": "Database error"}

    def send_email(self, to_email):
        """Sends an email and returns a tuple (email, success_status)."""
        message = Mail(
            from_email=From(settings.DEFAULT_FROM_EMAIL),
            to_emails=To(to_email),
            subject=settings.EMAIL_SUBJECT,
            plain_text_content=settings.EMAIL_MESSAGE,
        )

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            return (to_email, response.status_code in [200, 202])  # Return email & success status
        except Exception:
            return (to_email, False)

    def get(self, request, *args, **kwargs):
        """Handles GET request to send emails."""
        current_date = datetime.now()
        if (current_date - self.start_date).days >= self.day_limit:
            return JsonResponse({"message": "Email sending limit reached"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_list = self.fetch_emails()
        if recipient_list is None:
            return JsonResponse({"message": "No active users found to send emails"}, status=status.HTTP_404_NOT_FOUND)
        if isinstance(recipient_list, dict) and "error" in recipient_list:
            return JsonResponse({"message": recipient_list["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send emails in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            results = list(executor.map(self.send_email, recipient_list))

        success_count = sum(1 for _, success in results if success)
        failure_list = [email for email, success in results if not success]

        if not failure_list:
            return JsonResponse({"message": "Emails sent successfully"}, status=status.HTTP_200_OK)
        elif success_count == 0:
            return JsonResponse({"message": "Failed to send emails", "failed_emails": failure_list}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JsonResponse(
                {
                    "message": f"Partial success: {success_count} emails sent, {len(failure_list)} failed",
                    "failed_emails": failure_list
                },
                status=status.HTTP_207_MULTI_STATUS
            )


class SendSuccessEmail(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            to_email = data.get('email')
            points = data.get('points')

            if not to_email:
                return JsonResponse({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            if points is None:
                return JsonResponse({"message": "Points are required"}, status=status.HTTP_400_BAD_REQUEST)

            subject = "🌟 You've Earned Rewards for Your Recycling Efforts! ♻️"
            success_message = f"""Dear User,

We have some fantastic news for you! 🎉 Your dedication to recycling has made a meaningful impact, and as a token of our appreciation, we’ve added {points} reward points to your account. 💚

🌿 Your Actions Matter!

✔ Every item you recycle helps reduce waste and protect our environment. 🌎  
✔ Small steps lead to a greener, cleaner future for everyone.  
✔ Your contributions inspire others to join the movement!  

Keep up the incredible work—you’re not just recycling; you’re making a difference! 💪✨

Want to earn more points? Continue recycling and stay tuned for exciting rewards coming your way!

If you have any questions or need assistance, we’re always here to help. Feel free to reach out anytime. 📩

Thank you for being a sustainability champion! ♻️🌍

Best regards,  
**The Recycling Team**  

P.S. Share your achievements with friends and encourage them to recycle too—together, we can create a brighter future! 🚀
"""

            # Prepare the email
            message = Mail(
                from_email=From(settings.DEFAULT_FROM_EMAIL),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=success_message,
            )

            # Send the email using SendGrid
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)

                if response.status_code in [200, 202]:
                    return JsonResponse(
                        {"message": "Email sent successfully", "email": to_email},
                        status=status.HTTP_200_OK
                    )
                else:
                    return JsonResponse(
                        {
                            "message": "Failed to send email",
                            "email": to_email,
                            "error": "Unexpected response from SendGrid"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            except Exception as e:
                return JsonResponse(
                    {
                        "message": "Failed to send email",
                        "email": to_email,
                        "error": str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendFailureEmail(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            to_email = data.get('email')
            reason = data.get('reason', 'The uploaded image did not meet our guidelines.')  # Default reason

            if not to_email:
                return JsonResponse({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            subject = "⚠️ Image Upload Issue – Please Try Again!"
            failure_message = f"""Dear User,

Thank you for your recent image upload. Unfortunately, we couldn't process it due to the following reason:

🚫 **{reason}**  

We encourage you to try again with a valid image that meets our requirements.

🔹 Please ensure that:
- The image is clear and original.
- You are not reuploading the same image.
- The image is not sourced from the internet (e.g., Google Images).

Your contributions are valuable, and we truly appreciate your efforts! 🙌 If you need any assistance, feel free to reach out.  

Looking forward to your next upload!  

Best regards,  
**The Support Team**  

P.S. If you believe this was a mistake, please contact our support team. We're happy to assist you! 📩
"""

            # Prepare the email
            message = Mail(
                from_email=From(settings.DEFAULT_FROM_EMAIL),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=failure_message,
            )

            # Send the email using SendGrid
            try:
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)

                if response.status_code in [200, 202]:
                    return JsonResponse(
                        {"message": "Failure email sent successfully", "email": to_email},
                        status=status.HTTP_200_OK
                    )
                else:
                    return JsonResponse(
                        {
                            "message": "Failed to send failure email",
                            "email": to_email,
                            "error": "Unexpected response from SendGrid"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            except Exception as e:
                return JsonResponse(
                    {
                        "message": "Failed to send failure email",
                        "email": to_email,
                        "error": str(e)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"message": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
