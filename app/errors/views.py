from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Errors


# Create your views here.

class ErrorHandler:
    error_codes = {
        400: 'ошибка 400',
        403: 'ошибка 403',
        404: 'ошибка 404',
        500: 'ошибка 500'
    }

    def __init__(self, status_code):
        self.status_code = status_code
        self.error_name = ErrorHandler.error_codes.get(status_code)

    def get_error_context(self):
        errors = Errors.objects.filter(slug=f"kazhetsya-chto-to-poshlo-ne-tak-{self.status_code}")

        if errors:
            error = errors.first()
            return {
                'name': error.name,
                'image_path': error.image_path
            }
        return {}

    def handle_error(self, request, exception=None):
        context = self.get_error_context()
        return render(request, 'errors/error.html', context=context)


class EngineeringWorks(TemplateView):
    template_name = 'errors/error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj_error = Errors.objects.filter(slug="vedutsya-tehnicheskie-raboty")

        context["name"] = obj_error[0].name
        context["image_path"] = obj_error[0].image_path

        return context
