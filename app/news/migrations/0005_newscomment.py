# Generated by Django 4.2.21 on 2025-06-04 23:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0004_news_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата и время')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news_comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='news.news', verbose_name='Новость')),
            ],
            options={
                'verbose_name': 'Комментарий к новости',
                'verbose_name_plural': 'Комментарии к новостям',
                'ordering': ['-created_at'],
            },
        ),
    ]
