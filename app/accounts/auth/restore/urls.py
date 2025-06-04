from django.urls import path
from .views import (
    RestorePasswordStep1View,
    RestorePasswordStep1DoneView,
    RestorePasswordStep2View,
    RestorePasswordStep2DoneView
)

urlpatterns = [
    path('', RestorePasswordStep1View.as_view(), name='restore'),
    path('done/', RestorePasswordStep1DoneView.as_view(), name='restore_done'),
    path(
        '<uidb64>/<token>/',
        RestorePasswordStep2View.as_view(),
        name='restore_confirm'
    ),
    path('complete/', RestorePasswordStep2DoneView.as_view(), name='restore_complete'),
]