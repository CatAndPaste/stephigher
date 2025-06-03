from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView

from blog.models import BlogPost
from news.models import News
from pages.utils.mixins import SeoContextMixin


# Create your views here.
class HomePageView(SeoContextMixin, TemplateView):
    template_name = 'index.html'
    seo_title = 'Главная страница — StepHigher'
    seo_description = 'Читайте популярные статьи и свежие новости на StepHigher'
    seo_keywords = 'статьи, новости, StepHigher, блог, технологии'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['posts'] = BlogPost.objects.select_related('author').prefetch_related('tags')[:3]
        # Последние новости
        context['latest_news'] = News.objects.select_related('author').prefetch_related('tags').order_by('-published_at')[:5]
        # Популярные статьи (по количеству лайков)
        context['popular_posts'] = BlogPost.objects.annotate(likes_count=Count('liked_by')).order_by('-likes_count', '-published_at')[:3]
        return context
