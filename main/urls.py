from django.urls import path
from . import views

urlpatterns = [
    # Главная страница приложения
    path('', views.index, name='index'),
    # Страница конкретного вуза. <int:university_id> захватывает целое число и передаёт в представление
    path('university/<int:university_id>/', views.university_detail, name='university_detail'),
]