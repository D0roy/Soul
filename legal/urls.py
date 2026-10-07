from django.urls import path

from .views import (
    OfferView,
    PrivacyView,
    ConsentView,
    TermsView,
    )


app_name = "legal"

urlpatterns = [
    path("privacy/", PrivacyView.as_view(), name="privacy"),
    path("consent/", ConsentView.as_view(), name="consent"),
    path("offer/", OfferView.as_view(), name="offer"),
    path("terms/", TermsView.as_view(), name="terms"),
]