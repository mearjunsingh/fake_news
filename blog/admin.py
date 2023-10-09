from typing import Any
from django.contrib import admin
from .models import Blog, Category


from django.forms import ModelForm


class BlogAdminForm(ModelForm):
    class Meta:
        model = Blog
        fields = "__all__"


# Register your models here.
class BlogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "list_date",
        "views",
        "is_published",
    ]
    list_display_links = [
        "title",
    ]
    list_filter = ["category", "views", "list_date"]
    search_fields = ["title"]
    list_per_page = 50
    exclude = ["views", "slug"]

    form = BlogAdminForm


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
