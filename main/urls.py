from django.urls import path
from . import views

urlpatterns = [
    # Главная страница приложения
    path('', views.index, name='index'),
    # Страница конкретного вуза. <int:university_id> захватывает целое число и передаёт в представление
    path('university/<int:university_id>/', views.university_detail, name='university_detail'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]