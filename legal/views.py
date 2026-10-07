from django.views.generic import TemplateView

class PrivacyView(TemplateView):
    template_name = "legal/privacy.html"


class ConsentView(TemplateView):
    template_name = "legal/consent.html"


class OfferView(TemplateView):
    template_name = "legal/offer.html"


class TermsView(TemplateView):
    template_name = "legal/terms.html"