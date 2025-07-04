from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.db.models import F
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from pages.utils.mixins import SeoContextMixin

from .forms import CommentForm
from .models import BlogPost, Tag, Comment

COMMENTS_PER_LOAD = 5


class BlogListView(SeoContextMixin, ListView):
    model = BlogPost
    template_name = 'blog/main.html'
    context_object_name = 'posts'
    paginate_by = 12

    # SEO
    seo_title = 'RaftLab - Блог'
    seo_description = 'Читайте популярные статьи и свежие новости на RaftLab'
    seo_keywords = 'статьи, новости, StepHigher, RaftLab, блог, технологии'

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

        # pages my pages
        page_obj = ctx.get('page_obj')
        if page_obj is not None:
            total = page_obj.paginator.num_pages
            current = page_obj.number

            def build_page_sequence(current, total):
                if total <= 1:
                    return [1]
                left_bound = 3
                right_bound = total - 2

                if current <= left_bound:
                    seq = list(range(1, left_bound + 2)) + ['...', total]
                elif current >= right_bound:
                    seq = [1, '...'] + list(range(right_bound - 1, total + 1))
                else:
                    seq = [1, '...', current - 1, current, current + 1, '...', total]

                if len(seq) >= total:
                    return list(range(1, total + 1))
                return seq

            ctx['page_sequence'] = build_page_sequence(current, total)
        else:
            ctx['page_sequence'] = []

        return ctx


class BlogDetailView(SeoContextMixin, DetailView):
    model = BlogPost
    template_name = 'blog/post.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    seo_title = 'Блог — RaftLab'
    seo_description = 'Читайте популярные статьи и свежие новости на RaftLab'
    seo_keywords = 'статьи, новости, StepHigher, RaftLab, блог, технологии'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.object

        ctx['comment_form'] = CommentForm()

        all_comments = post.comments.all()
        paginator = Paginator(all_comments, COMMENTS_PER_LOAD)
        page_number = 1
        page_obj = paginator.get_page(page_number)

        ctx['comments'] = page_obj.object_list
        ctx['comments_page_number'] = page_number
        ctx['comments_num_pages'] = paginator.num_pages
        ctx['total_comments'] = paginator.count

        ctx['recommended_posts'] = (
            # random!
            BlogPost.objects
            .exclude(pk=post.pk)
            .order_by('?')[:3]
        )
        return ctx

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        post = self.object

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.created_at = timezone.now()
            comment.save()
            messages.success(request, "Комментарий добавлен!")
            return redirect(f"{reverse('blog_detail', args=[post.slug])}#comments")
        else:
            ctx = self.get_context_data()
            ctx['comment_form'] = form
            return render(request, self.template_name, ctx)


def toggle_like(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    user = request.user

    if not user or not user.is_authenticated:
        login_url = (reverse('login'))
        if request.headers.get('Hx-Request') == 'true':
            resp = HttpResponse(status=403)
            resp['HX-Redirect'] = login_url
            return resp
        return redirect(login_url)

    if user in post.liked_by.all():
        post.liked_by.remove(user)
    else:
        post.liked_by.add(user)

    context = {
        'post': post,
        'user': user,
    }
    return render(request, 'blog/partials/like_button.html', context)


@require_GET
def load_more_comments(request, slug):
    """
    AJAX-request, returns: { 'html': '...', 'has_next': True/False }
    """
    post = get_object_or_404(BlogPost, slug=slug)
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
        'blog/partials/comments_list.html',
        {
            'comments': comments_list,
            'user': request.user,
        },
        request=request
    )

    return JsonResponse({'html': html, 'has_next': page_obj.has_next()})

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("Нельзя удалять чужие комментарии!")

    post_slug = comment.post.slug
    comment.delete()
    return redirect(f"{reverse('blog_detail', args=[post_slug])}#comments")

