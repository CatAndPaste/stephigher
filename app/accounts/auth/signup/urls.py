from django.urls import path

from .views import *

urlpatterns = [
    path('', signup_step1, name='signup'),
    path('verify/', signup_step2, name='signup_verify'),
    path('password/', signup_step3, name='signup_password'),
]
