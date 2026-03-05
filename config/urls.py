from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Маршруты аутентификации (логин, логаут, сброс пароля и т.д.)
    path('accounts/', include('django.contrib.auth.urls')),
    # Страница регистрации
    path('accounts/register/', main_views.register, name='register'),
    # Основные страницы приложения
    path('', include('main.urls')),
]
