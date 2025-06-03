from django.views.generic import DetailView

from pages.utils.mixins import SeoContextMixin
from .models import BlogPost


# Create your views here.


class BlogDetailView(SeoContextMixin, DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    seo_title = 'Главная страница — StepHigher'
    seo_description = 'Читайте популярные статьи и свежие новости на StepHigher'
    seo_keywords = 'статьи, новости, StepHigher, блог, технологии'
