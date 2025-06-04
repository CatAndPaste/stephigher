from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView
from django.db.models import F
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from pages.utils.mixins import SeoContextMixin

from .models import News, Tag, NewsComment
from .forms import NewsCommentForm

COMMENTS_PER_LOAD = 5


class NewsListView(SeoContextMixin, ListView):
    model = News
    template_name = 'news/main.html'
    context_object_name = 'news_list'
    paginate_by = 5

    # SEO:
    seo_title = 'StepHigher – Новости'
    seo_description = 'Актуальные новости по Raft на StepHigher'
    seo_keywords = 'новости, StepHigher, Raft'

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort', 'desc')
        if sort == 'asc':
            qs = qs.order_by(F('published_at').asc())
        else:
            qs = qs.order_by(F('published_at').desc())

        # Фильтр по тегу
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
        ctx['all_tags'] = Tag.objects.all().order_by('name')
        return ctx


class NewsDetailView(SeoContextMixin, DetailView):
    model = News
    template_name = 'news/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    seo_title = 'Новости — StepHigher'
    seo_description = 'Актуальные новости по Raft на StepHigher'
    seo_keywords = 'новости, StepHigher, Raft'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object

        ctx['comment_form'] = NewsCommentForm()

        all_comments = post.comments.all()
        paginator = Paginator(all_comments, COMMENTS_PER_LOAD)
        page_number = 1
        page_obj = paginator.get_page(page_number)

        ctx['comments'] = page_obj.object_list
        ctx['comments_page_number'] = page_number
        ctx['comments_num_pages'] = paginator.num_pages
        ctx['total_comments'] = paginator.count


        ctx['recommended_posts'] = (
            # latest
            News.objects
            .exclude(pk=post.pk)
            .order_by('-published_at')[:2]
        )
        return ctx

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        post = self.object

        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.created_at = timezone.now()
            comment.save()
            messages.success(request, "Комментарий добавлен!")
            return redirect(f"{reverse('news_detail', args=[post.slug])}#comments")
        else:
            ctx = self.get_context_data()
            ctx['comment_form'] = form
            return render(request, self.template_name, ctx)


@require_GET
def news_load_more_comments(request, slug):
    """
    AJAX-запрос: {'html': '…', 'has_next': True/False}
    """
    post = get_object_or_404(News, slug=slug)
    page = request.GET.get('page')
    try:
        page_number = int(page)
        if page_number < 1:
            raise ValueError
    except (TypeError, ValueError):
        raise Http404

    all_comments = post.comments.all()
    paginator = Paginator(all_comments, COMMENTS_PER_LOAD)

    if page_number > paginator.num_pages:
        return JsonResponse({'html': '', 'has_next': False})

    page_obj = paginator.get_page(page_number)
    comments_list = page_obj.object_list

    html = render_to_string(
        'news/partials/comments_list.html',
        {
            'comments': comments_list,
            'user': request.user,
        },
        request=request
    )
    return JsonResponse({'html': html, 'has_next': page_obj.has_next()})


@login_required
@require_POST
def news_delete_comment(request, comment_id):
    comment = get_object_or_404(NewsComment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("Нельзя удалять чужие комментарии!")

    post_slug = comment.post.slug
    comment.delete()
    return redirect(f"{reverse('news_detail', args=[post_slug])}#comments")
