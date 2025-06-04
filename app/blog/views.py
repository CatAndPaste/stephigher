from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.db.models import F

from pages.utils.mixins import SeoContextMixin

from .models import BlogPost, Tag


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
            qs = qs.order_by(F('published_at').asc())
        else:
            qs = qs.order_by(F('published_at').desc())

        tag_name = self.request.GET.get('tag')
        if tag_name:
            try:
                tag = Tag.objects.get(name__iexact=tag_name)
            except Tag.DoesNotExist:
                return qs.none()
            qs = qs.filter(tags=tag)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_sort'] = self.request.GET.get('sort', 'desc')
        ctx['filter_by_tag'] = self.request.GET.get('tag', '')
        # TODO: add tags list
        ctx['all_tags'] = Tag.objects.all().order_by('name')
        return ctx


class BlogDetailView(SeoContextMixin, DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    seo_title = 'Главная страница — StepHigher'
    seo_description = 'Читайте популярные статьи и свежие новости на StepHigher'
    seo_keywords = 'статьи, новости, StepHigher, блог, технологии'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # random posts!
        ctx['recommended_posts'] = (
            BlogPost.objects
            .exclude(pk=self.object.pk)
            .order_by('?')[:3]
        )
        return ctx

@login_required
def toggle_like(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    user = request.user

    if user in post.liked_by.all():
        post.liked_by.remove(user)
    else:
        post.liked_by.add(user)

    context = {
        'post': post,
        'user': user,
    }
    return render(request, 'blog/partials/like_button.html', context)
