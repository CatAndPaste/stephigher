from django.db import models
from django.contrib.auth import get_user_model
from django_ckeditor_5.fields import CKEditor5Field
from filer.fields.image import FilerImageField

from pages.models import SeoMixin

# Create your models here.

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тег")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class News(SeoMixin, models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug')
    short_description = models.TextField("Краткое описание", max_length=500)
    full_description = CKEditor5Field(verbose_name='Описание', config_name='extends', blank=True, null=True)
    image = FilerImageField(
        verbose_name="Картинка",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_images"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги", related_name="news_items")
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Автор", related_name="news")
    liked_by = models.ManyToManyField(User, blank=True, related_name="liked_news", verbose_name="Понравилось")

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.liked_by.count()
