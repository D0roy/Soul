from django.shortcuts import redirect, render
from django.contrib.auth import logout, get_user_model
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import json

from django.conf import settings
from pywebpush import webpush, WebPushException

from .forms import ProfileForm, RegisterForm, LoginForm
from .tokens import email_verification_token
from .models import Profile, PushSubscription
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
    template_name = "accounts/register.html"
    success_url = reverse_lazy(
        "accounts:bio",
    )

    def form_valid(self, form):
        user = form.save(
            commit=False,
        )

        user.email = form.cleaned_data[
            "email"
        ]
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(
            force_bytes(user.pk),
        )

        token = email_verification_token.make_token(
            user,
        )

        verification_path = reverse(
            "accounts:verify_email",
            kwargs={
                "uidb64": uid,
                "token": token,
            },
        )

        verification_url = (
            settings.SITE_URL.rstrip("/")
            + verification_path
        )

        send_mail(
            subject="Подтверждение электронной почты",
            message=(
                "Здравствуйте!\n\n"
                "Чтобы подтвердить электронную почту, "
                "перейдите по ссылке:\n\n"
                f"{verification_url}\n\n"
                "Если вы не регистрировались на сайте, "
                "проигнорируйте это письмо."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                user.email,
            ],
            fail_silently=False,
        )

        return redirect(
            "accounts:verification_sent",
        )

class VerificationSentView(TemplateView):
    template_name = (
        "accounts/verification_sent.html"
    )

class VerifyEmailView(View):
    def get(
        self,
        request,
        uidb64,
        token,
    ):
        try:
            uid = urlsafe_base64_decode(
                uidb64,
            ).decode()

            user = User.objects.get(
                pk=uid,
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            user = None

        if (
            user is not None
            and email_verification_token.check_token(
                user,
                token,
            )
        ):
            user.is_active = True
            user.save(
                update_fields=[
                    "is_active",
                ],
            )

            return redirect(
                "accounts:login",
            )

        return render(
            request,
            "accounts/verification_invalid.html",
        )

class MyLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.get_redirect_url()

        if next_url:
            return next_url

        try:
            profile = self.request.user.profile
        except Profile.DoesNotExist:
            return reverse(
                "accounts:bio",
            )

        if not profile.display_name.strip():
            return reverse(
                "accounts:bio",
            )

        return reverse(
            "accounts:about-me",
        )


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class BioView(
    LoginRequiredMixin,
    UpdateView,
):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/settings.html"
    success_url = reverse_lazy(
        "accounts:about-me",
    )

    def get_object(self, queryset=None):
        profile, created = (
            Profile.objects.get_or_create(
                user=self.request.user,
            )
        )

        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs,
        )

        context["vapid_public_key"] = (
            settings.VAPID_PUBLIC_KEY
        )

        return context

    def post(self, request, *args, **kwargs):
        print("POST:", request.POST)
        print("FILES:", request.FILES)

        return super().post(
            request,
            *args,
            **kwargs,
        )

    def form_valid(self, form):
        print(
            "FORM CLEANED DATA:",
            form.cleaned_data,
            flush=True,
        )

        form.instance.user = (
            self.request.user
        )

        self.object = form.save()

        print(
            "SAVED AVATAR:",
            self.object.avatar.name,
            flush=True,
        )

        return redirect(
            self.get_success_url()
        )

    def form_invalid(self, form):
        print(
            "FORM ERRORS:",
            form.errors.as_json(),
            flush=True,
        )

        print(
            "FORM NON FIELD ERRORS:",
            form.non_field_errors(),
            flush=True,
        )

        return super().form_invalid(form)


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
                notification_type=Notification.TYPE_QUESTION,
                question__isnull=False,
            )
            .exclude(
                question_id__in=answered_question_ids,
            )
            .select_related("question")
            .order_by("-created_at")
        )

        return context

@login_required
@require_POST
def save_push_subscription(request):
    try:
        data = json.loads(request.body)

        endpoint = data.get("endpoint")
        keys = data.get("keys", {})

        p256dh = keys.get("p256dh")
        auth = keys.get("auth")

        if not endpoint or not p256dh or not auth:
            return JsonResponse(
                {
                    "error": "Некорректная push-подписка",
                },
                status=400,
            )

        subscription, created = (
            PushSubscription.objects.update_or_create(
                endpoint=endpoint,
                defaults={
                    "user": request.user,
                    "p256dh": p256dh,
                    "auth": auth,
                    "is_active": True,
                },
            )
        )

        profile, created = Profile.objects.get_or_create(
            user=request.user,
        )

        profile.notifications_enabled = True

        profile.save(
            update_fields=["notifications_enabled"],
        )

        return JsonResponse(
            {
                "success": True,
                "created": created,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "error": "Некорректный JSON",
            },
            status=400,
        )

@login_required
@require_POST
def disable_push_notifications(request):
    PushSubscription.objects.filter(
        user=request.user,
    ).update(
        is_active=False,
    )

    request.user.profile.notifications_enabled = False
    request.user.profile.save(
        update_fields=["notifications_enabled"],
    )

    return JsonResponse(
        {
            "success": True,
        }
    )

def service_worker(request):
    service_worker_path = (
        settings.BASE_DIR
        / "static"
        / "service-worker.js"
    )

    content = service_worker_path.read_text(
        encoding="utf-8",
    )

    return HttpResponse(
        content,
        content_type="application/javascript",
    )

@login_required
@require_POST
def send_test_push(request):
    subscriptions = PushSubscription.objects.filter(
        user=request.user,
        is_active=True,
    )

    sent = 0
    failed = 0

    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }

        payload = json.dumps(
            {
                "title": "Soul",
                "body": "Тестовое уведомление работает.",
                "url": "/accounts/notifications/",
            }
        )

        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=(
                    settings.VAPID_PRIVATE_KEY
                ),
                vapid_claims={
                    "sub": settings.VAPID_ADMIN_EMAIL,
                },
            )

            sent += 1

        except WebPushException:
            failed += 1

    return JsonResponse(
        {
            "sent": sent,
            "failed": failed,
        }
    )