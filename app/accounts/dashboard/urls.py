from django.urls import path
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('', favorites_view, name='dashboard'),

    path('favorites/', favorites_view, name='favorites'),
    path('user-info/', user_info_view, name='user_info'),
    path('settings/', settings_view, name='settings'),
]