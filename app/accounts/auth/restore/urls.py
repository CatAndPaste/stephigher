from django.urls import path
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

urlpatterns = [
    path('', CustomPasswordResetView.as_view(), name='restore'),
    path('done/', CustomPasswordResetDoneView.as_view(), name='restore_done'),
    path(
        '<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(),
        name='restore_confirm'
    ),
    path('complete/', CustomPasswordResetCompleteView.as_view(), name='restore_complete'),
]