from django.db import models
from django.contrib.auth.models import User

class University(models.Model):
    """Модель университета"""
    name = models.CharField(
        max_length=255,
        verbose_name='Название вуза'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,  # может быть пустым
        help_text='Краткое описание университета'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город'
    )
    website = models.URLField(
        max_length=255,
        verbose_name='Официальный сайт',
        blank=True,  # необязательное поле
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    rating = models.FloatField(
        default=0.0,
        verbose_name='Рейтинг'
    )
    image = models.ImageField(
        upload_to='universities/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    def update_rating(self):
        """Пересчитывает рейтинг на основе опубликованных отзывов"""
        published_reviews = self.reviews.filter(moderated=True)
        if published_reviews.exists():
            avg = published_reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg, 2)  # округляем до двух знаков
        else:
            self.rating = 0.0
        self.save(update_fields=['rating'])

    class Meta:
        verbose_name = 'Университет'
        verbose_name_plural = 'Университеты'
        ordering = ['-created_at']  # сортировка по умолчанию: новые сверху

    def __str__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Университет'
    )
    # Вместо author_name:
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        null=True,  # временно разрешаем NULL, чтобы можно было применить миграцию
        blank=True
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
    moderated = models.BooleanField(default=False, verbose_name='Прошел модерацию')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['author', 'university'], name='unique_review_per_user_per_university')
        ]

    def __str__(self):
        return f'Отзыв от {self.author.username if self.author else "Аноним"} о {self.university.name}'

    def update_rating(self):
        """Пересчёт рейтинга на основе опубликованных отзывов"""
        published_reviews = self.faculty_reviews.filter(moderated=True)
        avg = published_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.rating = round(avg, 2) if avg is not None else 0.0
        self.save(update_fields=['rating'])

class Faculty(models.Model):
    """Модель факультета"""
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='faculties',
        verbose_name='Университет'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.university.name})'

    def update_rating(self):
        """Пересчёт рейтинга на основе опубликованных отзывов"""
        published_reviews = self.faculty_reviews.filter(moderated=True)
        avg = published_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.rating = round(avg, 2) if avg is not None else 0.0
        self.save(update_fields=['rating'])

class Teacher(models.Model):
    """Модель преподавателя"""
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    description = models.TextField(blank=True, verbose_name='Описание')
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='teachers',
        verbose_name='Университет'
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        verbose_name='Факультет'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def update_rating(self):
        published_reviews = self.teacher_reviews.filter(moderated=True)
        avg = published_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.rating = round(avg, 2) if avg is not None else 0.0
        self.save(update_fields=['rating'])


class Specialty(models.Model):
    """Модель специальности (направления подготовки)"""
    name = models.CharField(max_length=255, verbose_name='Название')
    code = models.CharField(max_length=20, blank=True, verbose_name='Код специальности')
    description = models.TextField(blank=True, verbose_name='Описание')
    universities = models.ManyToManyField(University, related_name='specialties', blank=True)
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='specialties',
        verbose_name='Факультет (опционально)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'
        ordering = ['name']

    def __str__(self):
        uni_names = ', '.join([uni.name for uni in self.universities.all()[:2]])
        if self.universities.count() > 2:
            uni_names += '...'
        return f'{self.name} (вузы: {uni_names})'

    def update_rating(self):
        published_reviews = self.specialty_reviews.filter(moderated=True)
        avg = published_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.rating = round(avg, 2) if avg is not None else 0.0
        self.save(update_fields=['rating'])


class SpecialtyReview(models.Model):
    """Отзыв на специальность"""
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='specialty_reviews',
        verbose_name='Специальность'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='specialty_reviews',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
    moderated = models.BooleanField(default=False, verbose_name='Прошел модерацию')

    class Meta:
        verbose_name = 'Отзыв на специальность'
        verbose_name_plural = 'Отзывы на специальности'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['author', 'specialty'], name='unique_specialty_review_per_user')
        ]

    def __str__(self):
        return f'Отзыв от {self.author} о специальности {self.specialty.name}'


class TeacherReview(models.Model):
    """Отзыв на преподавателя"""
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='teacher_reviews',
        verbose_name='Преподаватель'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_reviews',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
    moderated = models.BooleanField(default=False, verbose_name='Прошел модерацию')

    class Meta:
        verbose_name = 'Отзыв на преподавателя'
        verbose_name_plural = 'Отзывы на преподавателей'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['author', 'teacher'], name='unique_teacher_review_per_user')
        ]

    def __str__(self):
        return f'Отзыв от {self.author} о преподавателе {self.teacher.last_name} {self.teacher.first_name}'
