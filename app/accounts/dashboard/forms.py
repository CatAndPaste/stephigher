import re
import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings

from accounts.models import User

# TODO: merge validators with signup


class UserInfoForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=3,
        label="Имя пользователя",
        help_text="От 3 до 16 символов",
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    email = forms.EmailField(
        max_length=150,
        label="Email",
        help_text="Введите адрес электронной почты",
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    new_password1 = forms.CharField(
        required=False,
        label="Новый пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        required=False,
        label="Повторите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    email_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=False,
        label="Код подтверждения email",
        help_text="Введите код подтверждения, отправленный на новый адрес",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )

    error_messages = {
        'password_mismatch': "Пароли не совпадают",
        'username_exists': "Извините, это имя пользователя уже занято",
        'email_exists': "Извините, этот email уже зарегистрирован",
        'email_code_required': "Пожалуйста введите код подтверждения, отправленный на новый email",
        'email_code_invalid': "Неверный код подтверждения email",
        'email_code_mismatch': "Введённый код не совпадает с отправленным",
        'email_code_expired': "Время действия кода подтверждения email истекло",
    }

    def __init__(self, *args, user=None, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.session = session or {}

        if self.session.get('new_email'):
            self.fields['email'].initial = self.session['new_email']
        else:
            self.fields['email'].initial = user.email

        self.fields['username'].initial = user.username

        if self.session.get('new_email'):
            self.fields['email_code'].required = True
        else:
            self.fields['email_code'].widget = forms.HiddenInput()
            self.fields['email_code'].required = False

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        username = re.sub(r'\s+', ' ', username)

        if len(username) < 3:
            raise ValidationError(
                "Имя пользователя должно быть длиннее 3 символов!",
                code='invalid_username'
            )
        if len(username) > 16:
            raise ValidationError(
                "Имя пользователя не может быть длиннее 16 символов!",
                code='invalid_username'
            )

        if not re.match(r'^[A-Za-zА-Яа-я0-9_\s\-]+$', username):
            raise ValidationError(
                "Имя пользователя может содержать только латинские или кириллические буквы, "
                "цифры, -, _ и пробелы!",
                code='invalid_username'
            )

        if User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                self.error_messages['username_exists'],
                code='username_exists'
            )
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email == self.user.email:
            return email

        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                self.error_messages['email_exists'],
                code='email_exists'
            )
        return email

    def clean_email_code(self):
        code = self.cleaned_data.get('email_code')
        new_email = self.session.get('new_email')
        saved_code = self.session.get('email_code')
        ts = self.session.get('email_code_ts')

        if not new_email:
            return ''

        if not code:
            raise ValidationError(self.error_messages['email_code_required'], code='email_code_required')

        now_ts = datetime.datetime.now().timestamp()
        if not ts or (now_ts - ts > settings.SIGNUP_CODE_EXPIRATION_SECONDS):
            raise ValidationError(self.error_messages['email_code_expired'], code='email_code_expired')

        if code != saved_code:
            raise ValidationError(self.error_messages['email_code_mismatch'], code='email_code_mismatch')
        return code

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('new_password1')
        pw2 = cleaned_data.get('new_password2')

        if pw1 or pw2:
            if not pw1:
                self.add_error('new_password1', "Введите новый пароль")
            elif not pw2:
                self.add_error('new_password2', "Пожалуйста повторите пароль")
            elif pw1 != pw2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch'
                )
            else:
                try:
                    validate_password(pw1, user=self.user)
                except ValidationError as e:
                    self.add_error('new_password1', e.messages)

        return cleaned_data

    def save(self):
        user = self.user
        data = self.cleaned_data

        new_username = data.get('username')
        new_email = data.get('email')
        pw1 = data.get('new_password1')

        if new_username and new_username != user.username:
            user.username = new_username

        if self.session.get('new_email'):
            new_email = data.get('email')
            if new_email == self.session.get('new_email'):
                user.email = new_email

        if pw1:
            user.set_password(pw1)

        user.save()

        if self.session:
            for key in ('new_email', 'email_code', 'email_code_ts'):
                if key in self.session:
                    del self.session[key]

        return user


class SettingsForm(forms.Form):
    email_subscriber = forms.BooleanField(
        required=False,
        label="Получать информационные рассылки?",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['email_subscriber'].initial = user.email_subscriber

    def save(self):
        self.user.email_subscriber = self.cleaned_data['email_subscriber']
        self.user.save()
        return self.user
