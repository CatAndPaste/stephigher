from django.db import models


# Create your models here.
class SeoMixin(models.Model):
    seo_title = models.CharField("SEO Title", max_length=255, blank=True)
    seo_description = models.TextField("SEO Description", max_length=500, blank=True)
    seo_keywords = models.CharField("SEO Keywords", max_length=255, blank=True)

    class Meta:
        abstract = True
