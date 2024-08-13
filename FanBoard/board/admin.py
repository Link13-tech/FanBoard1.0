from django.contrib import admin
from .models import Post, Response


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'post_time')
    search_fields = ('title', 'content')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'response_time')
    search_fields = ('content',)
