from django.urls import path
from django.contrib.auth.views import LoginView


from .views import (
    AboutMeView,
    RegisterView,
    MyLogoutView,
    BioView,
    DeleteAccountView,
    NotificationsView,
    UserProfileView,
    )

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html", redirect_authenticated_user=True, ), name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("user/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("register/", RegisterView.as_view(), name="register"),
    path("bio/", BioView.as_view(template_name = "accounts/bio.html"), name="bio"),
    path("settings/", BioView.as_view(template_name = "accounts/settings.html"), name="settings"),
    path("notifications/", NotificationsView.as_view(), name="notifications"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
]