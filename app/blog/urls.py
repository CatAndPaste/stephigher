from django.urls import path
from .views import BlogDetailView, BlogListView, toggle_like, load_more_comments, delete_comment

urlpatterns = [
    path('', BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('<slug:slug>/toggle-like/', toggle_like, name='toggle_like'),
    path('<slug:slug>/comments/', load_more_comments, name='blog_post_load_comments'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='blog_post_delete_comment'),
]
