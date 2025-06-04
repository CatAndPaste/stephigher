import re
import datetime
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from accounts.models import User

class Step1Form(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=3,
        label="Имя пользователя",
        help_text="От 3 до 16 символов",
    )
    email = forms.EmailField(
        max_length=150,
        label="Email",
        help_text="Введите адрес электронной почты",
    )
    accept_rules = forms.BooleanField(
        label="Я принимаю правила сайта",
        error_messages={'required': "Вы должны принять правила сайта!"},
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        # many spaces to one space
        username = re.sub(r'\s+', ' ', username)

        if len(username) < 3:
            raise ValidationError(
                "Имя пользователя должно быть длиннее трёх символов!",
                code='invalid_username'
            )
        if len(username) > 16:
            raise ValidationError(
                "Имя пользователя не может быть длиннее шестнадцати символов!",
                code='invalid_username'
            )

        # latin + cyrillic, spaces, -, _
        if not re.match(r'^[A-Za-zА-Яа-я0-9_\s\-]+$', username):
            raise ValidationError(
                _("Имя пользователя может содержать только латинские или кириллические буквы, цифры, -, _ и пробелы!"),
                code='invalid_username'
            )

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                "Простите, имя уже занято!", code='username_exists'
            )
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "Пользователь с таким email уже зарегистрирован", code='email_exists'
            )
        return email


class Step2Form(forms.Form):
    code = forms.CharField(
        max_length=20,
        min_length=1,
        label="На вашу почту отправлено письмо с кодом подтверждения",
        help_text="Введите код из письма",
        strip=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    error_messages = {
        'invalid_code': "Неверный код. Проверьте и попробуйте снова",
        'expired_code': "Время проверки кода истекло. Пожалуйста начните регистрацию заново",
    }

    def __init__(self, *args, session=None, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    def clean_code(self):
        entered = self.cleaned_data.get('code')
        if not self.session:
            raise ValidationError(self.error_messages['expired_code'], code='expired_code')

        saved = self.session.get('reg_code')
        timestamp = self.session.get('reg_code_ts')

        if not saved or not timestamp:
            raise ValidationError(self.error_messages['expired_code'], code='expired_code')

        now = datetime.datetime.now().timestamp()
        if now - timestamp > settings.SIGNUP_CODE_EXPIRATION_SECONDS:
            raise ValidationError(self.error_messages['expired_code'], code='expired_code')

        if entered != saved:
            raise ValidationError(self.error_messages['invalid_code'], code='invalid_code')

        return entered


class Step3Form(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        dummy_user = User(username='', email='')
        super().__init__(dummy_user, *args, **kwargs)

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        return password


