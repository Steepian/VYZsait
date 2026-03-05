from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import University, Review
from .forms import ReviewForm

def index(request):
    """Главная страница со списком вузов"""
    universities = University.objects.all()
    context = {
        'universities': universities,
    }
    return render(request, 'index.html', context)

def university_detail(request, university_id):
    university = get_object_or_404(University, pk=university_id)
    reviews = university.reviews.filter(moderated=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.university = university
            review.author = request.user  
            review.save()
            return redirect('university_detail', university_id=university.id)
    else:
        form = ReviewForm()

    context = {
        'university': university,
        'reviews': reviews,
        'form': form,
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