from django.urls import path
from .views import ImageProcessingView


urlpatterns = [
    path('process-image/', ImageProcessingView.as_view(), name='process_image'),
]
