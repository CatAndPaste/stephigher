from django.urls import path

from .views import *

urlpatterns = [
    path('engineering_works/', EngineeringWorks.as_view(), name='engineering_works'),
]
