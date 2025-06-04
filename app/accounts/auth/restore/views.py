from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings

from .forms import EmailOnlyForm

from accounts.models import User


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/auth/restore/step1.html'
    form_class = EmailOnlyForm
    email_template_name = 'email/restore/reset_link.txt'
    html_email_template_name = 'email/restore/reset_link.html'
    subject_template_name = 'email/restore/subject.txt'

    success_url = reverse_lazy('restore_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = form.get_users(email)

        if users:
            form.save(
                use_https=self.request.is_secure(),
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


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/auth/restore/step1_done.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['email'] = self.request.GET.get('email', '')
        return ctx


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/auth/restore/step2.html'
    success_url = reverse_lazy('restore_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/auth/restore/step2_done.html'