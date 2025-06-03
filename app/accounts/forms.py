from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseCreationForm, UserChangeForm as BaseChangeForm
from .models import User


class UserCreationForm(BaseCreationForm):
    class Meta(BaseCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class UserChangeForm(BaseChangeForm):
    class Meta(BaseChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
