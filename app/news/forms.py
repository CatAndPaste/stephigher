from django import forms
from .models import NewsComment


class NewsCommentForm(forms.ModelForm):
    class Meta:
        model = NewsComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите комментарий...'
            }),
        }
        labels = {
            'text': ''
        }