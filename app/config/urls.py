"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from errors.views import ErrorHandler

urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # path('robots.txt', TemplateView.as_view(template_name="other/robots.txt", content_type="text/plain")),
    # path('', include('accounts.urls')),
    path('', include('pages.urls')),
    path('', include('errors.urls')),
    path('', include('blog.urls')),
    # path('', include('help.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = ErrorHandler(400).handle_error
handler403 = ErrorHandler(403).handle_error
handler404 = ErrorHandler(404).handle_error
handler500 = ErrorHandler(500).handle_error
