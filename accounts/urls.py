from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from .forms import RussianSetPasswordForm

from .views import (
    MyLoginView,
    AboutMeView,
    RegisterView,
    VerificationSentView,
    VerifyEmailView,
    MyLogoutView,
    BioView,
    DeleteAccountView,
    NotificationsView,
    UserProfileView,
    DeleteAvatarView,
    save_push_subscription,
    disable_push_notifications,
    service_worker,
    send_test_push
    )

app_name = "accounts"

urlpatterns = [
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("verification-sent/", VerificationSentView.as_view(), name="verification_sent"),
    path("verify/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name=("accounts/password_reset.html"),
            email_template_name=("accounts/password_reset_email.txt"),
            subject_template_name=("accounts/password_reset_subject.txt"),
            success_url=reverse_lazy("accounts:password_reset_done",),
        ),
        name="password_reset",
    ),
    path("password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name=("accounts/password_reset_done.html"),
        ),
        name="password_reset_done",
    ),
    path("password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name=(
                "accounts/password_reset_confirm.html"
            ),
            form_class=RussianSetPasswordForm,
            success_url=reverse_lazy(
                "accounts:password_reset_complete",
            ),
        ),
        name="password_reset_confirm",
    ),
    path("password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name=("accounts/password_reset_complete.html"),
        ),
        name="password_reset_complete",
    ),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("user/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("bio/", BioView.as_view(template_name = "accounts/bio.html"), name="bio"),
    path("settings/", BioView.as_view(template_name = "accounts/settings.html"), name="settings"),
    path("notifications/", NotificationsView.as_view(), name="notifications"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
    path("push/subscribe/", save_push_subscription, name="push-subscribe"),
    path("push/disable/", disable_push_notifications, name="push-disable"),
    path("service-worker.js", service_worker, name="service-worker"),
    path("push/test/", send_test_push, name="push-test"),
]