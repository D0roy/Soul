from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction

from .models import CoupleInvite, Couple
from questions.models import Question, Answer
from notifications.models import Notification
from notifications.services import create_notification

User = get_user_model()

class UserSearchPageView(LoginRequiredMixin, TemplateView):
    template_name = "couples/search_user.html"


class UserAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get(
            "q",
            "",
        ).strip()

        if not query:
            return JsonResponse(
                {
                    "users": [],
                }
            )

        users = (
            User.objects
            .filter(
                Q(username__icontains=query)
                | Q(
                    profile__display_name__icontains=query
                )
            )
            .exclude(
                pk=request.user.pk,
            )
            .select_related("profile")
            .order_by("username")[:10]
        )

        results = []

        for user in users:
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

            partner = None

            if couple is not None:
                if couple.user1_id == user.id:
                    partner = couple.user2
                else:
                    partner = couple.user1

            profile = getattr(
                user,
                "profile",
                None,
            )

            results.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": (
                        profile.display_name
                        if (
                            profile
                            and profile.display_name
                        )
                        else user.username
                    ),
                    "avatar_url": (
                        profile.avatar.url
                        if (
                            profile
                            and profile.avatar
                        )
                        else ""
                    ),
                    "partner": (
                        {
                            "id": partner.id,
                            "username": partner.username,
                            "display_name": (
                                partner.profile.display_name
                                if (
                                    hasattr(
                                        partner,
                                        "profile",
                                    )
                                    and partner.profile.display_name
                                )
                                else partner.username
                            ),
                        }
                        if partner
                        else None
                    ),
                }
            )

        return JsonResponse(
            {
                "users": results,
            }
        )

class SendInviteView(LoginRequiredMixin, View):
    def post(self, request, user_id, *args, **kwargs):
        recipient = get_object_or_404(
            User,
            pk=user_id,
        )

        if recipient == request.user:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Нельзя пригласить самого себя.",
                },
                status=400,
            )

        invite, created = CoupleInvite.objects.get_or_create(
            sender=request.user,
            recipient=recipient,
        )

        if created:
            create_notification(
                user=invite.recipient,
                notification_type=Notification.TYPE_INVITE,
                title="Приглашение в пару",
                message=(
                    f"{invite.sender.username} "
                    "отправил вам приглашение в пару."
                ),
                url="/accounts/notifications/",
            )

            message = "Приглашение отправлено."
        else:
            message = "Приглашение уже отправлялось."

        return JsonResponse({
            "success": True,
            "message": message,
        })

class DeleteInviteView(LoginRequiredMixin, View):
    def post(self, request, invite_id):
        invite = get_object_or_404(
            CoupleInvite,
            id=invite_id,
            sender=request.user,
            status=CoupleInvite.Status.PENDING,
        )

        invite.delete()
        return redirect("accounts:notifications")

class InviteAnswer(
    LoginRequiredMixin,
    View,
):
    def post(self, request, invite_id):
        invite = get_object_or_404(
            CoupleInvite,
            id=invite_id,
            recipient=request.user,
            status=CoupleInvite.Status.PENDING,
        )

        answer = request.POST.get(
            "answer",
        )

        if answer == "False":
            invite.status = (
                CoupleInvite.Status.REJECTED
            )

            invite.save(
                update_fields=["status"],
            )

            invite.delete()

            return JsonResponse(
                {
                    "success": True,
                    "message": (
                        "Приглашение отклонено"
                    ),
                }
            )

        if answer != "True":
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Некорректный ответ"
                    ),
                },
                status=400,
            )

        has_couple = Couple.objects.filter(
            Q(user1=request.user)
            | Q(user2=request.user)
        ).exists()

        confirmed = (
            request.POST.get(
                "confirm_replace",
            )
            == "1"
        )

        if has_couple and not confirmed:
            return JsonResponse(
                {
                    "success": False,
                    "confirm_required": True,
                    "message": (
                        "У вас уже есть пара. "
                        "После принятия приглашения "
                        "старая связь будет разорвана."
                    ),
                },
                status=409,
            )

        with transaction.atomic():
            Couple.objects.filter(
                Q(user1=invite.sender)
                | Q(user2=invite.sender)
                | Q(user1=invite.recipient)
                | Q(user2=invite.recipient)
            ).delete()

            Couple.objects.create(
                user1=invite.sender,
                user2=invite.recipient,
            )

            invite.status = (
                CoupleInvite.Status.ACCEPTED
            )

            invite.save(
                update_fields=["status"],
            )

            invite.delete()

        return JsonResponse(
            {
                "success": True,
                "message": (
                    "Пара создана. "
                    "Старая связь разорвана."
                ),
            }
        )

class DeleteCoupleView(LoginRequiredMixin, View):
    def post(self, request):
        partner_id = request.POST.get("partner_id")
        user = self.request.user
        couple = (
            Couple.objects
            .filter(
                (Q(user1=request.user) & Q(user2_id=partner_id))
                | (Q(user2=request.user) & Q(user1_id=partner_id))
            )
            .first()
        )

        couple_answers = Answer.objects.filter(
            user=request.user,
            question__couple_question=True,
        )

        couple_answers.delete()

        couple.delete()
        return redirect("accounts:about-me")