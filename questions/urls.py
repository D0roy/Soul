from django.urls import path
from django.contrib.auth.views import LoginView

from .views import (
    QuestionCreateView,
    CategoryCreateView,
    QuestionListView,
    QuestionAnswerView
    )

app_name = "questions"

urlpatterns = [
    path("create/", QuestionCreateView.as_view(), name="question-create"),
    path("categories/create/", CategoryCreateView.as_view(), name="category-create"),
    path("list/", QuestionListView.as_view(), name="question-list"),
    path("question/<int:question_id>/", QuestionAnswerView.as_view(), name="question"),
]