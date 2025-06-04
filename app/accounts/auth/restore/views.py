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

from .forms import EmailOnlyForm

from accounts.models import User


class RestorePasswordStep1View(PasswordResetView):
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['email'] = self.request.GET.get('email', '')
        return ctx


class RestorePasswordStep2View(PasswordResetConfirmView):
    template_name = 'accounts/auth/restore/step2.html'
    success_url = reverse_lazy('restore_complete')

    def dispatch(self, request, uidb64=None, token=None, *args, **kwargs):
        user = self.get_user(uidb64)
        if user is None or not self.token_generator.check_token(user, token):
            messages.error(request, "Недействительная ссылка для сброса пароля! Пожалуйста проверьте, что вы "
                                    "скопировали ссылку полностью или попробуйте ещё раз")
            return redirect('restore')
        return super().dispatch(request, uidb64=uidb64, token=token, *args, **kwargs)


class RestorePasswordStep2DoneView(PasswordResetCompleteView):
    template_name = 'accounts/auth/restore/step2_done.html'