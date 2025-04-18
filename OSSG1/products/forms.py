# forms.py
from django import forms
from users.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'placeholder': '请输入评分（1-5）'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入评价内容'
            }),
        }
        labels = {
            'rating': '评分 (1-5)',
            'comment': '评价内容',
        }
