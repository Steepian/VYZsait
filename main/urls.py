from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('university/<int:university_id>/', views.university_detail, name='university_detail'),
    path('specialty/<int:specialty_id>/', views.specialty_detail, name='specialty_detail'),
    path('teacher/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('faculty/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),

    # Редактирование/удаление отзывов
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('specialty-review/<int:review_id>/edit/', views.edit_specialty_review, name='edit_specialty_review'),
    path('specialty-review/<int:review_id>/delete/', views.delete_specialty_review, name='delete_specialty_review'),
    path('teacher-review/<int:review_id>/edit/', views.edit_teacher_review, name='edit_teacher_review'),
    path('teacher-review/<int:review_id>/delete/', views.delete_teacher_review, name='delete_teacher_review'),

    path('my-reviews/', views.my_reviews, name='my_reviews'),

    path('specialties/', views.specialty_list, name='specialty_list'),
    path('teachers/', views.teachers_list, name='teachers_list'),
]