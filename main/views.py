from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import University, Review, Faculty, Teacher, TeacherReview, Specialty, SpecialtyReview
from .forms import ReviewForm, TeacherReviewForm, SpecialtyReviewForm
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
        'specialties': university.specialties.all(),      
        'teachers': university.teachers.all(),        
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
    reviews_university = Review.objects.filter(author=request.user).order_by('-created_at')
    reviews_specialty = SpecialtyReview.objects.filter(author=request.user).order_by('-created_at')
    reviews_teacher = TeacherReview.objects.filter(author=request.user).order_by('-created_at')
    
    # Объединяем в список с аннотацией типа
    combined = []
    for r in reviews_university:
        combined.append({
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'created_at': r.created_at,
            'moderated': r.moderated,
            'target_type': 'university',
            'target_name': r.university.name,
            'target_id': r.university.id,
            'url_name': 'university_detail',
        })
    for r in reviews_specialty:
        combined.append({
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'created_at': r.created_at,
            'moderated': r.moderated,
            'target_type': 'specialty',
            'target_name': f"{r.specialty.name} ({r.specialty.university.name})",
            'target_id': r.specialty.id,
            'url_name': 'specialty_detail',
        })
    for r in reviews_teacher:
        combined.append({
            'id': r.id,
            'text': r.text,
            'rating': r.rating,
            'created_at': r.created_at,
            'moderated': r.moderated,
            'target_type': 'teacher',
            'target_name': f"{r.teacher.last_name} {r.teacher.first_name} ({r.teacher.university.name})",
            'target_id': r.teacher.id,
            'url_name': 'teacher_detail',
        })
    
    # Сортируем по дате (новые сверху)
    combined.sort(key=lambda x: x['created_at'], reverse=True)
    paginator = Paginator(combined, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'my_reviews.html', {'page_obj': page_obj})

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

def teachers_list(request):
    """Список всех преподавателей с поиском"""
    teachers_list = Teacher.objects.all().select_related('university', 'faculty')
    
    query = request.GET.get('q')
    if query:
        teachers_list = teachers_list.filter(
            models.Q(last_name__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(university__name__icontains=query) |
            models.Q(faculty__name__icontains=query)
        )
    
    teachers_list = teachers_list.order_by('university__name', 'last_name', 'first_name')
    
    paginator = Paginator(teachers_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'teachers_list.html', {'page_obj': page_obj, 'query': query})

def specialty_detail(request, specialty_id):
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    reviews_all = specialty.specialty_reviews.filter(moderated=True).order_by('-created_at')
    paginator = Paginator(reviews_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_review = None
    if request.user.is_authenticated:
        user_review = SpecialtyReview.objects.filter(specialty=specialty, author=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')
        if user_review:
            messages.error(request, 'Вы уже оставили отзыв для этой специальности.')
            return redirect('specialty_detail', specialty_id=specialty.id)

        form = SpecialtyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.specialty = specialty
            review.author = request.user
            try:
                review.save()
                messages.success(request, 'Отзыв добавлен и ожидает модерации.')
            except IntegrityError:
                messages.error(request, 'Не удалось добавить отзыв. Возможно, вы уже оставляли его.')
            return redirect('specialty_detail', specialty_id=specialty.id) + '#reviews'
    else:
        form = SpecialtyReviewForm()

    context = {
        'specialty': specialty,
        'page_obj': page_obj,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'specialty_detail.html', context)


def specialty_list(request):
    specialties = Specialty.objects.all().prefetch_related('universities').select_related('faculty')
    query = request.GET.get('q')
    if query:
        specialties = specialties.filter(
            Q(name__icontains=query) | Q(code__icontains=query) | Q(universities__name__icontains=query)
        ).distinct()  # distinct, чтобы избежать дублей при фильтрации по ManyToMany
    paginator = Paginator(specialties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'specialty_list.html', context)


@login_required
def edit_specialty_review(request, review_id):
    review = get_object_or_404(SpecialtyReview, pk=review_id, author=request.user)
    if request.method == 'POST':
        form = SpecialtyReviewForm(request.POST, instance=review)
        if form.is_valid():
            review.moderated = False
            form.save()
            messages.success(request, 'Отзыв обновлён. Он будет проверен администратором.')
            url = reverse('specialty_detail', args=[review.specialty.id]) + '#reviews'
            return redirect(url)
    else:
        form = SpecialtyReviewForm(instance=review)
    return render(request, 'edit_specialty_review.html', {'form': form, 'review': review})


@login_required
def delete_specialty_review(request, review_id):
    review = get_object_or_404(SpecialtyReview, pk=review_id, author=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён.')
        url = reverse('specialty_detail', args=[review.specialty.id]) + '#reviews'
        return redirect(url)
    return render(request, 'delete_specialty_review.html', {'review': review})

def faculty_detail(request, faculty_id):
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    teachers = faculty.teachers.all()
    return render(request, 'faculty_detail.html', {'faculty': faculty, 'teachers': teachers})