from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'id': 'email',
            'placeholder': 'Введите адрес электронной почты'
        })
    )

    password = forms.CharField(
        label=_('Пароль'),
        strip=False,
        widget=forms.PasswordInput
    )

    error_messages = {
        'invalid_login': "Мы не нашли ни одного аккаунта, соответствующего такой паре Email и пароль!",
        'inactive': "Аккаунт неактивен, пожалуйста проверьте почту.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            else:
                if not self.user.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
        return self.cleaned_data

    def get_user(self):
        return self.user
