from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import University, Review
from .forms import ReviewForm
from django.core.paginator import Paginator
from django.db import models
from django.urls import reverse
from django.db import IntegrityError
from django.contrib import messages

def index(request):
    """Главная страница со списком вузов"""
    universities = University.objects.all()
    query = request.GET.get('q')
    if query:
        universities = universities.filter(
            models.Q(name__icontains=query) | models.Q(city__icontains=query)
        )
    universities = universities.order_by('-rating', 'name')
    context = {
        'universities': universities,
    }
    return render(request, 'index.html', context)

def university_detail(request, university_id):
    university = get_object_or_404(University, pk=university_id)
    
    # Все опубликованные отзывы (для пагинации)
    reviews_all = university.reviews.filter(moderated=True).order_by('-created_at')
    paginator = Paginator(reviews_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Проверяем, есть ли у текущего пользователя отзыв для этого вуза (включая немодерированные)
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(
            university=university,
            author=request.user
        ).first()   # берём первый, хотя ограничение уникальности гарантирует один
    
    # Обработка POST (создание нового отзыва) – только если у пользователя ещё нет отзыва
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        if user_review:
            # Если отзыв уже есть, не даём создать новый
            messages.error(request, 'Вы уже оставили отзыв для этого вуза.')
            return redirect('university_detail', university_id=university.id)
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.university = university
            review.author = request.user
            try:
                review.save()
                messages.success(request, 'Отзыв добавлен и ожидает модерации.')
            except IntegrityError:
                messages.error(request, 'Не удалось добавить отзыв. Возможно, вы уже оставляли его.')
            url = reverse('university_detail', args=[review.university.id]) + '#reviews'
            return redirect(url)
    else:
        form = ReviewForm()
    
    context = {
        'university': university,
        'page_obj': page_obj,
        'form': form,
        'user_review': user_review,   # передаём в шаблон
    }
    return render(request, 'university_detail.html', context)

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически входим после регистрации
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, author=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            # Сбрасываем модерацию – после редактирования отзыв снова должен проверяться
            review.moderated = False
            # Сохраняем форму (она обновит все поля, включая moderated)
            form.save()
            messages.success(request, 'Отзыв обновлён. Он будет проверен администратором.')
            url = reverse('university_detail', args=[review.university.id]) + '#reviews'
            return redirect(url)
    else:
        form = ReviewForm(instance=review)

    context = {'form': form, 'review': review}
    return render(request, 'edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """
    Удаление отзыва. Доступно только автору.
    GET: показывает страницу подтверждения.
    POST: удаляет отзыв и перенаправляет на страницу вуза.
    """
    review = get_object_or_404(Review, pk=review_id, author=request.user)
    university_id = review.university.id

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён.')
        url = reverse('university_detail', args=[university_id]) + '#reviews'
        return redirect(url)
    else:
        context = {'review': review}
        return render(request, 'delete_review.html', context)