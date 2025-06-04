from django.urls import path
from .views import BlogDetailView, BlogListView, toggle_like

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('<slug:slug>/toggle-like/', toggle_like, name='toggle_like'),
]
