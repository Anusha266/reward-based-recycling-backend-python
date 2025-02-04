

# views.py (inside your app)

from django.http import HttpResponse
from django.views import View

class homePage(View):
    def get(self, request, *args, **kwargs):
        # Return a simple welcome message
        return HttpResponse("Welcome to Reward-based Recycling Tracker")
