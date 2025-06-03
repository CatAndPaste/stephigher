from django.contrib import admin
from .models import *


# Register your models here.


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_path')
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Errors, ErrorAdmin)
