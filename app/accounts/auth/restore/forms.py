from django import forms
from django.contrib.auth.forms import PasswordResetForm


class EmailOnlyForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email
