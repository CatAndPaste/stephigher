class SeoContextMixin:
    seo_title = ''
    seo_description = ''
    seo_keywords = ''

    def get_seo_title(self):
        return self.seo_title

    def get_seo_description(self):
        return self.seo_description

    def get_seo_keywords(self):
        return self.seo_keywords

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_title'] = self.get_seo_title()
        context['default_description'] = self.get_seo_description()
        context['default_keywords'] = self.get_seo_keywords()
        return context
