from zoneinfo import ZoneInfo

from django.utils import timezone


class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                timezone_name = (
                    request.user.profile.timezone
                    or "UTC"
                )

                timezone.activate(
                    ZoneInfo(timezone_name)
                )

            except Exception:
                timezone.activate(
                    ZoneInfo("UTC")
                )
        else:
            timezone.deactivate()

        response = self.get_response(request)

        timezone.deactivate()

        return response