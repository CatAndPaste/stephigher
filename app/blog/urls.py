from django.urls import path
from .views import BlogDetailView

urlpatterns = [
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
]
