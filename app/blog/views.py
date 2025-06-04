from django.views.generic import DetailView
from django.views.generic import ListView
from django.db.models import F
from pages.utils.mixins import SeoContextMixin
from .models import BlogPost


class BlogListView(SeoContextMixin, ListView):
    model = BlogPost
    template_name = 'blog/main.html'
    context_object_name = 'posts'
    paginate_by = 10

    # SEO
    seo_title = 'StepHigher - Блог'
    seo_description = 'Читайте популярные статьи и свежие новости на StepHigher'
    seo_keywords = 'статьи, новости, StepHigher, блог, технологии'

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort', 'desc')
        if sort == 'asc':
            return qs.order_by(F('published_at').asc())
        return qs.order_by(F('published_at').desc())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_sort'] = self.request.GET.get('sort', 'desc')
        return ctx


class BlogDetailView(SeoContextMixin, DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    seo_title = 'Главная страница — StepHigher'
    seo_description = 'Читайте популярные статьи и свежие новости на StepHigher'
    seo_keywords = 'статьи, новости, StepHigher, блог, технологии'
