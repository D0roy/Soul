from django import forms

from .models import Category, Question


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        labels = {
            "name": "Название категории",
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "text",
            "category",
            "is_active",
            "can_repeat",
            "couple_question"
        ]
        labels = {
            "text": "Текст вопроса",
            "category": "Категория",
            "is_active": "Активный вопрос",
            "can_repeat": "Можно задавать повторно",
        }

from django import forms

from .models import Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        labels = {
            "text": "Ваш ответ",
        }
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": (
                        "Напишите свой ответ..."
                    ),
                },
            ),
        }