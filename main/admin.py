from django.contrib import admin
from django.utils.html import mark_safe
from .models import University, Review, Faculty, Teacher, FacultyReview, TeacherReview

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'rating', 'created_at', 'image_preview')
    list_filter = ('city',)
    search_fields = ('name', 'city')
    fields = ('name', 'description', 'city', 'website', 'image')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return '-'
    image_preview.short_description = 'Изображение'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'university', 'rating', 'created_at', 'moderated')
    list_filter = ('moderated', 'rating', 'university')
    search_fields = ('author__username', 'text')
    actions = ['approve_reviews']

    def author_username(self, obj):
        return obj.author.username if obj.author else 'Аноним'
    author_username.short_description = 'Автор'

    def approve_reviews(self, request, queryset):
        queryset.update(moderated=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'rating', 'created_at')
    list_filter = ('university',)
    search_fields = ('name', 'university__name')
    fields = ('name', 'description', 'university')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'university', 'faculty', 'rating', 'created_at')
    list_filter = ('university', 'faculty')
    search_fields = ('last_name', 'first_name', 'university__name')
    fields = ('first_name', 'last_name', 'description', 'university', 'faculty')


@admin.register(FacultyReview)
class FacultyReviewAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'faculty', 'rating', 'created_at', 'moderated')
    list_filter = ('moderated', 'rating', 'faculty')
    search_fields = ('author__username', 'text')
    actions = ['approve_reviews']

    def author_username(self, obj):
        return obj.author.username if obj.author else 'Аноним'
    author_username.short_description = 'Автор'

    def approve_reviews(self, request, queryset):
        queryset.update(moderated=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"


@admin.register(TeacherReview)
class TeacherReviewAdmin(admin.ModelAdmin):
    list_display = ('author_username', 'teacher', 'rating', 'created_at', 'moderated')
    list_filter = ('moderated', 'rating', 'teacher')
    search_fields = ('author__username', 'text')
    actions = ['approve_reviews']

    def author_username(self, obj):
        return obj.author.username if obj.author else 'Аноним'
    author_username.short_description = 'Автор'

    def approve_reviews(self, request, queryset):
        queryset.update(moderated=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"