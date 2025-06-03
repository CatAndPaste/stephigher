from django.contrib.auth.views import LoginView
from .forms import EmailAuthenticationForm


class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = 'accounts/auth/login/auth.html'
    redirect_authenticated_user = True
