from django.db import models


# Create your models here.
class Errors(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название ошибки')
    image_path = models.FileField(upload_to='error_images/', verbose_name='Путь к фото')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Slug')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ошибки'
        verbose_name_plural = 'Ошибки'
