from django.contrib import admin
from django.utils.text import slugify

from .models import News, Tag


# Register your models here.

def generate_unique_slug(title, model):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
    return slug


def duplicate_news(modeladmin, request, queryset):
    for obj in queryset:
        tags = obj.tags.all()
        obj.pk = None  # сбрасываем ID
        obj.title += " (копия)"
        obj.slug = generate_unique_slug(obj.title, News)  # уникальный slug
        obj.save()
        obj.tags.set(tags)


duplicate_news.short_description = "Дублировать выбранные новости"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    actions = [duplicate_news]

    list_display = ('title', 'author', 'published_at', 'total_likes_display')
    list_filter = ('author', 'published_at', 'tags')
    search_fields = ('title', 'short_description', 'full_description')
    autocomplete_fields = ('tags', 'author')
    filter_horizontal = ('liked_by',)
    readonly_fields = ('published_at',)
    raw_id_fields = ('image',)

    prepopulated_fields = {'slug': ('title',)}

    def total_likes_display(self, obj):
        return obj.total_likes()

    total_likes_display.short_description = '❤️ Лайков'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
