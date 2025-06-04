from django.urls import path, include

urlpatterns = [
    path('', include('accounts.auth.login.urls')),
    path('signup/', include('accounts.auth.signup.urls')),
]