from django.urls import path
from .views import *

urlpatterns = [
    path('', NewsListView.as_view(), name='news_list'),
    path('<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('<slug:slug>/comments/', news_load_more_comments, name='news_load_more_comments'),
    path('comment/<int:comment_id>/delete/', news_delete_comment, name='news_delete_comment'),
]