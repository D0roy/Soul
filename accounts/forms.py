from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import Profile

class ProfileImageInput(
    forms.ClearableFileInput,
):
    template_name = (
        "widgets/clearable_file_input.html"
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = [
            "avatar",
            "display_name",
            "gender",
            "birth_date",
            "city",
            "zodiac_sign",
            "bio",
            "notifications_enabled",
            "timezone",
        ]

        labels = {
            "avatar": "Фото профиля",
            "display_name": "Имя",
            "gender": "Пол",
            "birth_date": "Дата рождения",
            "city": "Город",
            "zodiac_sign": "Знак зодиака",
            "bio": "О себе",
            "notifications_enabled": (
                "Получать уведомления от сайта"
            ),
            "timezone": "Часовой пояс",
        }

        widgets = {
            "avatar": ProfileImageInput(
                attrs={
                    "class": "profile-file-input",
                }
            ),
            "birth_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                },
            ),
            "notifications_enabled": (
                forms.CheckboxInput(
                    attrs={
                        "class": (
                            "notifications-checkbox"
                        ),
                    }
                )
            ),
            "timezone": forms.HiddenInput(),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "birth_date"
        ].input_formats = [
            "%Y-%m-%d",
        ]

class RegisterForm(
    UserCreationForm,
):
    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

        labels = {
            "username": "Имя пользователя",
            "email": "Электронная почта",
        }

        help_texts = {
            "username": (
                "Введите имя пользователя."
            ),
            "email": (
                "Введите электронную почту."
            ),
        }

        error_messages = {
            "username": {
                "required": (
                    "Введите имя пользователя."
                ),
                "unique": (
                    "Пользователь с таким именем "
                    "уже существует."
                ),
            },
            "email": {
                "invalid": (
                    "Введите корректный адрес "
                    "электронной почты."
                ),
            },
        }


    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": (
                    "Введите пароль"
                ),
            }
        ),
        help_text=(
            "Пароль должен содержать не менее "
            "8 символов."
        ),
        error_messages={
            "required": (
                "Введите пароль."
            ),
        },
    )


    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": (
                    "Повторите пароль"
                ),
            }
        ),
        help_text=(
            "Введите пароль ещё раз."
        ),
        error_messages={
            "required": (
                "Повторите пароль."
            ),
        },
    )


    def clean_username(self):
        username = self.cleaned_data.get(
            "username"
        )

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "Пользователь с таким логином "
                "уже существует."
            )

        return username


    def clean_email(self):
        email = self.cleaned_data.get(
            "email"
        )

        if email and User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной "
                "почтой уже существует."
            )

        return email


    def clean_password2(self):
        password1 = self.cleaned_data.get(
            "password1"
        )

        password2 = self.cleaned_data.get(
            "password2"
        )

        if not password2:
            raise forms.ValidationError(
                "Повторите пароль."
            )

        if password1 != password2:
            raise forms.ValidationError(
                "Пароли не совпадают."
            )

        try:
            password_validation.validate_password(
                password2,
                self.instance,
            )
        except ValidationError:
            raise forms.ValidationError(
                self.get_password_error_text(
                    password2
                )
            )

        return password2


    @staticmethod
    def get_password_error_text(password):
        if len(password) < 8:
            return (
                "Пароль должен содержать не менее "
                "8 символов."
            )

        if password.isdigit():
            return (
                "Пароль не должен состоять только "
                "из цифр."
            )

        common_passwords = {
            "password",
            "password123",
            "qwerty",
            "qwerty123",
            "12345678",
            "123456789",
        }

        if password.lower() in common_passwords:
            return (
                "Этот пароль слишком простой. "
                "Придумайте более сложный пароль."
            )

        return (
            "Пароль не соответствует требованиям "
            "безопасности."
        )