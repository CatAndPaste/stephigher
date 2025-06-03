from django.urls import path, include

urlpatterns = [
    path('', include('accounts.auth.login.urls')),
]