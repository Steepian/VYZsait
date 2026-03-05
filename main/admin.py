from django.contrib import admin
from .models import University, Review

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created_at')
    list_filter = ('city',)
    search_fields = ('name', 'city')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Заменяем 'author_name' на 'author' (или лучше отобразить username)
    list_display = ('author_username', 'university', 'rating', 'created_at', 'moderated')
    list_filter = ('moderated', 'rating', 'university')
    search_fields = ('author__username', 'text')  # поиск по имени пользователя
    actions = ['approve_reviews']

    def author_username(self, obj):
        """Возвращает имя пользователя или 'Аноним', если автор не задан"""
        return obj.author.username if obj.author else 'Аноним'
    author_username.short_description = 'Автор'  # заголовок колонки

    def approve_reviews(self, request, queryset):
        queryset.update(moderated=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"