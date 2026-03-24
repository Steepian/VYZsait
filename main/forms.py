from django import forms
from .models import Review, FacultyReview, TeacherReview

class ReviewForm(forms.ModelForm):
    """
    Форма для добавления отзыва.
    Основана на модели Review, но включает только поля,
    которые должен заполнять пользователь.
    """
    class Meta:
        model = Review
        fields = ['text', 'rating']
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError('Отзыв должен быть содержательным (минимум 10 символов)')
        return text
    
class FacultyReviewForm(forms.ModelForm):
    class Meta:
        model = FacultyReview
        fields = ['text', 'rating']
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError('Отзыв должен быть содержательным (минимум 10 символов)')
        return text


class TeacherReviewForm(forms.ModelForm):
    class Meta:
        model = TeacherReview
        fields = ['text', 'rating']
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError('Отзыв должен быть содержательным (минимум 10 символов)')
        return text