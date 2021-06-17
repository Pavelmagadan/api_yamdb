from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin

from .models import Category, Comment, Genre, Review, Title, User


class UserAdmin(OriginalUserAdmin):
    fieldsets = tuple(
        (fieldset[0], {
            **{key: value for (key, value) in fieldset[1].items()
                if key != 'fields'},
            'fields': fieldset[1]['fields'] + ('bio', 'role')
        })
        if fieldset[0] == 'Personal info'
        else fieldset
        for fieldset in OriginalUserAdmin.fieldsets
    )
    list_display = ['email', 'username', 'role', 'is_active']
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    search_fields = ('name',)
    ordering = ('pk',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review_id', 'text', 'pub_date',)
    search_fields = ('author', 'text')
    ordering = ('-pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    search_fields = ('title',)
    ordering = ('pk',)
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'text', 'pub_date', 'score',)
    search_fields = ('author', 'text',)
    ordering = ('-pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category',)
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('pk',)
    empty_value_display = '-пусто-'
