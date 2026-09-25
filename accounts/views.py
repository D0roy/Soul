from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import Http404

from .forms import ProfileForm, RegisterForm
from .models import Profile
from couples.models import CoupleInvite, Couple
from notifications.models import Notification
from questions.models import Answer

User = get_user_model()

class AboutMeView(
    LoginRequiredMixin,
    TemplateView,
):
    template_name = "accounts/about-me.html"

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        user = self.request.user

        couple = (
            Couple.objects
            .filter(
                Q(user1=user)
                | Q(user2=user)
            )
            .select_related(
                "user1",
                "user2",
            )
            .first()
        )

        if couple is None:
            partner = None
        elif couple.user1_id == user.id:
            partner = couple.user2
        else:
            partner = couple.user1

        answered_questions = (
            Answer.objects
            .filter(
                user=user,
            )
            .select_related(
                "question",
            )
            .order_by(
                "-answer_date",
                "-id",
            )
        )

        context["partner"] = partner
        context["answered_questions"] = (
            answered_questions
        )

        return context

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = (
        "accounts/user-profile.html"
    )

    def get_profile_user(self):
        user_id = self.kwargs["user_id"]

        profile_user = (
            User.objects
            .select_related("profile")
            .filter(
                id=user_id,
            )
            .first()
        )

        if profile_user is None:
            raise Http404(
                "Пользователь не найден."
            )

        return profile_user

    def get_couple(self, user):
        return (
            Couple.objects
            .filter(
                (
                    Q(user1=self.request.user)
                    & Q(user2=user)
                )
                | (
                    Q(user2=self.request.user)
                    & Q(user1=user)
                )
            )
            .select_related(
                "user1",
                "user2",
            )
            .first()
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        current_user = self.request.user
        profile_user = self.get_profile_user()

        couple = self.get_couple(
            profile_user
        )

        if couple is None:
            raise PermissionDenied(
                "Профиль доступен только партнёру."
            )

        answered_questions = (
            Answer.objects
            .filter(
                user=profile_user,
            )
            .select_related(
                "question",
            )
            .order_by(
                "-answer_date",
                "-id",
            )
        )

        context["profile_user"] = profile_user
        context["partner"] = current_user
        context["answered_questions"] = (
            answered_questions
        )

        return context

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy("accounts:bio")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

class BioView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/bio.html"
    success_url = reverse_lazy("accounts:about-me")

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user

        logout(request)
        user.delete()

        return redirect("accounts:login")

class NotificationsView(
    LoginRequiredMixin,
    ListView,
):
    model = CoupleInvite
    template_name = (
        "accounts/notifications.html"
    )
    context_object_name = "invites"

    def get_queryset(self):
        return (
            CoupleInvite.objects
            .filter(
                Q(sender=self.request.user)
                | Q(recipient=self.request.user)
            )
            .select_related(
                "sender",
                "recipient",
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        answered_question_ids = (
            Answer.objects
            .filter(
                user=self.request.user,
            )
            .values_list(
                "question_id",
                flat=True,
            )
        )

        context["question_notifications"] = (
            Notification.objects
            .filter(
                user=self.request.user,
            )
            .exclude(
                question_id__in=answered_question_ids,
            )
            .select_related("question")
            .order_by("-created_at")
        )

        return context