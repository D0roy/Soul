from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.db.models import Q
from django.shortcuts import redirect, render

from django.utils import timezone
from zoneinfo import ZoneInfo

from .forms import QuestionForm, CategoryForm, AnswerForm
from .models import Question, Category, Answer
from couples.models import Couple

from notifications.models import Notification

class QuestionCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView,
):
    model = Question
    form_class = QuestionForm
    template_name = "questions/question_form.html"
    success_url = reverse_lazy(
        "questions:question-create",
    )

    def test_func(self):
        return self.request.user.username == "Doroy"

class CategoryCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView,
):
    model = Category
    form_class = CategoryForm
    template_name = "questions/category_form.html"
    success_url = reverse_lazy(
        "questions:question-create",
    )

    def test_func(self):
        return self.request.user.username == "Doroy"

class QuestionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Question
    template_name = "questions/questions_list.html"
    context_object_name = "questions"

    def test_func(self):
        return self.request.user.username == "Doroy"

    def get_queryset(self):
        return (
            Question.objects
            .filter(category__isnull=False)
            .select_related("category")
            .order_by(
                "category__name",
                "id",
            )
        )

class QuestionAnswerView(LoginRequiredMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = "questions/question.html"
    success_url = reverse_lazy(
        "accounts:notifications",
    )

    def get_partner(self):
        couple = (
            Couple.objects
            .filter(
                Q(user1=self.request.user)
                | Q(user2=self.request.user)
            )
            .select_related("user1", "user2")
            .first()
        )

        if couple is None:
            return None

        if couple.user1_id == self.request.user.id:
            return couple.user2

        return couple.user1

    def get_question(self):
        user = self.request.user
        partner = self.get_partner()

        questions = Question.objects.filter(
            id=self.kwargs["question_id"],
            is_active=True,
        )

        if partner is None:
            questions = questions.filter(
                couple_question=False,
            )

        questions = questions.exclude(
            can_repeat=False,
            answers__user=user,
        )

        return questions.first()

    def get(self, request, *args, **kwargs):
        question = self.get_question()

        if question is None:
            return render(
                request,
                "questions/no_questions.html",
            )

        return super().get(
            request,
            *args,
            **kwargs,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.get_question()
        return context

    def form_valid(self, form):
        question = self.get_question()

        if question is None:
            return redirect(
                "questions:no-questions",
            )


        try:
            user_timezone = ZoneInfo(
                self.request.user.profile.timezone
                or "UTC"
            )
        except Exception:
            user_timezone = ZoneInfo("UTC")


        local_now = timezone.now().astimezone(
            user_timezone
        )


        form.instance.user = (
            self.request.user
        )

        form.instance.question = question

        form.instance.answer_date = (
            local_now.date()
        )


        response = super().form_valid(
            form
        )


        Notification.objects.filter(
            user=self.request.user,
            question=question,
            is_read=False,
        ).update(
            is_read=True
        )


        return response