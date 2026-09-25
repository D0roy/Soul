from django.urls import path

from .views import (
    UserAutocompleteView,
    UserSearchPageView,
    SendInviteView,
    DeleteInviteView,
    InviteAnswer,
    DeleteCoupleView,
    )

app_name = "couples"

urlpatterns = [
    path("search/", UserSearchPageView.as_view(), name="search-page"),
    path("search/users/", UserAutocompleteView.as_view(), name="user-autocomplete"),
    path("invite/<int:user_id>/", SendInviteView.as_view(), name="send-invite"),
    path("delete-invite/<int:invite_id>/", DeleteInviteView.as_view(), name="delete-invite"),
    path("invite-answer/<int:invite_id>/", InviteAnswer.as_view(), name="invite-answer"),
    path("delete-couple/", DeleteCoupleView.as_view(), name="delete-couple"),
]