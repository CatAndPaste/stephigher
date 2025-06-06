from django.db import models
from django.contrib.auth import get_user_model
from django_ckeditor_5.fields import CKEditor5Field
from filer.fields.image import FilerImageField
from django.utils import timezone

from pages.models import SeoMixin

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class BlogPost(SeoMixin, models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug')
    short_description = models.TextField("Краткое описание", max_length=500)
    full_description = CKEditor5Field(verbose_name='Описание', config_name='extends', blank=True, null=True)
    image = FilerImageField(
        verbose_name="Картинка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_images"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги", related_name="posts")
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", related_name="blog_posts")
    liked_by = models.ManyToManyField(User, blank=True, related_name="liked_posts", verbose_name="Понравилось")

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.liked_by.count()


class Comment(models.Model):
    post = models.ForeignKey(
        'BlogPost',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата и время')

    class Meta:
        ordering = ['-created_at']  # От самых свежих к старым
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий {self.author} к посту "{self.post}"'
