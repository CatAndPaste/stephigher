from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from .forms import EmailOnlyForm

from accounts.models import User


class RestorePasswordStep1View(PasswordResetView):
    template_name = 'accounts/auth/restore/step1.html'
    form_class = EmailOnlyForm
    email_template_name = 'email/restore/reset_link.txt'
    html_email_template_name = 'email/restore/reset_link.html'
    subject_template_name = 'email/restore/subject.txt'

    success_url = reverse_lazy('restore_done')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = form.get_users(email)

        if users:
            form.save(
                domain_override=settings.SITE_NAME,
                use_https=True,
                token_generator=self.token_generator,
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name=self.email_template_name,
                html_email_template_name=self.html_email_template_name,
                subject_template_name=self.subject_template_name,
                request=self.request,
                extra_email_context={
                    'site_name': settings.SITE_NAME,
                }
            )

        return redirect(f"{self.success_url}?email={email}")


class RestorePasswordStep1DoneView(PasswordResetDoneView):
    template_name = 'accounts/auth/restore/step1_done.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['email'] = self.request.GET.get('email', 'ваш почтовый ящик')
        return ctx


class RestorePasswordStep2View(PasswordResetConfirmView):
    template_name = 'accounts/auth/restore/step2.html'
    success_url = reverse_lazy('restore_complete')

    def dispatch(self, request, uidb64=None, token=None, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().dispatch(request, uidb64=uidb64, token=token, *args, **kwargs)


class RestorePasswordStep2DoneView(PasswordResetCompleteView):
    template_name = 'accounts/auth/restore/step2_done.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)