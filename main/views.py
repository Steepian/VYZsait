from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import University, Review, Faculty, Teacher, FacultyReview, TeacherReview
from .forms import ReviewForm, FacultyReviewForm, TeacherReviewForm
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
    
    # Получаем факультеты и преподавателей этого вуза
    faculties = university.faculties.all()  
    teachers = university.teachers.all()    
    
    # Отзывы с пагинацией 
    reviews_all = university.reviews.filter(moderated=True).order_by('-created_at')
    paginator = Paginator(reviews_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(university=university, author=request.user).first()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        if user_review:
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
            return redirect('university_detail', university_id=university.id) + '#reviews'
    else:
        form = ReviewForm()
    
    context = {
        'university': university,
        'faculties': faculties,      
        'teachers': teachers,        
        'page_obj': page_obj,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'university_detail.html', context)

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
    
@login_required
def my_reviews(request):
    # Получаем отзывы разных типов
    university_reviews = Review.objects.filter(author=request.user).annotate(
        target_name=models.F('university__name'),
        target_type=models.Value('university', output_field=models.CharField()),
        target_id=models.F('university_id'),
        url_name=models.Value('university_detail', output_field=models.CharField()),
    ).values(
        'id', 'text', 'rating', 'created_at', 'moderated',
        'target_name', 'target_type', 'target_id', 'url_name'
    )

    faculty_reviews = FacultyReview.objects.filter(author=request.user).annotate(
        target_name=models.F('faculty__name'),
        target_type=models.Value('faculty', output_field=models.CharField()),
        target_id=models.F('faculty_id'),
        url_name=models.Value('faculty_detail', output_field=models.CharField()),
    ).values(
        'id', 'text', 'rating', 'created_at', 'moderated',
        'target_name', 'target_type', 'target_id', 'url_name'
    )

    teacher_reviews = TeacherReview.objects.filter(author=request.user).annotate(
        target_name=models.ExpressionWrapper(
            models.F('teacher__last_name') + models.Value(' ') + models.F('teacher__first_name'),
            output_field=models.CharField()
        ),
        target_type=models.Value('teacher', output_field=models.CharField()),
        target_id=models.F('teacher_id'),
        url_name=models.Value('teacher_detail', output_field=models.CharField()),
    ).values(
        'id', 'text', 'rating', 'created_at', 'moderated',
        'target_name', 'target_type', 'target_id', 'url_name'
    )

    # Объединяем три QuerySet в список и сортируем по дате
    all_reviews = list(university_reviews) + list(faculty_reviews) + list(teacher_reviews)
    all_reviews.sort(key=lambda x: x['created_at'], reverse=True)

    # Пагинация
    paginator = Paginator(all_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'my_reviews.html', {'page_obj': page_obj})

def faculty_detail(request, faculty_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    # Отзывы на факультет (опубликованные)
    reviews_all = faculty.faculty_reviews.filter(moderated=True).order_by('-created_at')
    paginator = Paginator(reviews_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Проверяем, есть ли у пользователя отзыв на этот факультет
    user_review = None
    if request.user.is_authenticated:
        user_review = FacultyReview.objects.filter(faculty=faculty, author=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        if user_review:
            messages.error(request, 'Вы уже оставили отзыв для этого факультета.')
            return redirect('faculty_detail', faculty_id=faculty.id)

        form = FacultyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.faculty = faculty
            review.author = request.user
            try:
                review.save()
                messages.success(request, 'Отзыв добавлен и ожидает модерации.')
            except IntegrityError:
                messages.error(request, 'Не удалось добавить отзыв. Возможно, вы уже оставляли его.')
            return redirect('faculty_detail', faculty_id=faculty.id) + '#reviews'
    else:
        form = FacultyReviewForm()

    context = {
        'faculty': faculty,
        'page_obj': page_obj,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'faculty_detail.html', context)


# Страница преподавателя
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    # Отзывы на преподавателя (опубликованные)
    reviews_all = teacher.teacher_reviews.filter(moderated=True).order_by('-created_at')
    paginator = Paginator(reviews_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_review = None
    if request.user.is_authenticated:
        user_review = TeacherReview.objects.filter(teacher=teacher, author=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        if user_review:
            messages.error(request, 'Вы уже оставили отзыв для этого преподавателя.')
            return redirect('teacher_detail', teacher_id=teacher.id)

        form = TeacherReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.teacher = teacher
            review.author = request.user
            try:
                review.save()
                messages.success(request, 'Отзыв добавлен и ожидает модерации.')
            except IntegrityError:
                messages.error(request, 'Не удалось добавить отзыв. Возможно, вы уже оставляли его.')
            return redirect('teacher_detail', teacher_id=teacher.id) + '#reviews'
    else:
        form = TeacherReviewForm()

    context = {
        'teacher': teacher,
        'page_obj': page_obj,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'teacher_detail.html', context)

@login_required
def edit_faculty_review(request, review_id):
    review = get_object_or_404(FacultyReview, pk=review_id, author=request.user)
    if request.method == 'POST':
        form = FacultyReviewForm(request.POST, instance=review)
        if form.is_valid():
            # При редактировании сбрасываем модерацию
            review.moderated = False
            form.save()
            messages.success(request, 'Отзыв обновлён. Он будет проверен администратором.')
            url = reverse('faculty_detail', args=[review.faculty.id]) + '#reviews'
            return redirect(url)
    else:
        form = FacultyReviewForm(instance=review)
    context = {'form': form, 'review': review}
    return render(request, 'edit_faculty_review.html', context)


@login_required
def delete_faculty_review(request, review_id):
    review = get_object_or_404(FacultyReview, pk=review_id, author=request.user)
    faculty_id = review.faculty.id
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён.')
        url = reverse('faculty_detail', args=[faculty_id]) + '#reviews'
        return redirect(url)
    context = {'review': review}
    return render(request, 'delete_faculty_review.html', context)


@login_required
def edit_teacher_review(request, review_id):
    review = get_object_or_404(TeacherReview, pk=review_id, author=request.user)
    if request.method == 'POST':
        form = TeacherReviewForm(request.POST, instance=review)
        if form.is_valid():
            review.moderated = False
            form.save()
            messages.success(request, 'Отзыв обновлён. Он будет проверен администратором.')
            url = reverse('teacher_detail', args=[review.teacher.id]) + '#reviews'
            return redirect(url)
    else:
        form = TeacherReviewForm(instance=review)
    context = {'form': form, 'review': review}
    return render(request, 'edit_teacher_review.html', context)


@login_required
def delete_teacher_review(request, review_id):
    review = get_object_or_404(TeacherReview, pk=review_id, author=request.user)
    teacher_id = review.teacher.id
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён.')
        url = reverse('teacher_detail', args=[teacher_id]) + '#reviews'
        return redirect(url)
    context = {'review': review}
    return render(request, 'delete_teacher_review.html', context)