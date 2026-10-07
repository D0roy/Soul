from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import Profile

class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": (
            "Пожалуйста, введите правильный "
            "логин или адрес электронной почты "
            "и пароль."
        ),
        "inactive": (
            "Ваш аккаунт не активирован. "
            "Подтвердите электронную почту "
            "по ссылке из письма."
        ),
    }

    username = forms.CharField(
        label="Логин или электронная почта",
        widget=forms.TextInput(
            attrs={
                "placeholder": (
                    "Введите логин или email"
                ),
                "autocomplete": "username",
            },
        ),
        error_messages={
            "required": (
                "Введите логин или электронную почту."
            ),
        },
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Введите пароль",
                "autocomplete": "current-password",
            },
        ),
        error_messages={
            "required": "Введите пароль.",
        },
    )

class ProfileImageInput(forms.FileInput):
    pass

class ProfileForm(
    forms.ModelForm,
):
    gender = forms.ChoiceField(
        label="Пол",
        choices=Profile.Gender.choices,
        required=False,
        widget=forms.RadioSelect(),
    )

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
                    "accept": "image/*",
                },
            ),
            "birth_date": forms.DateInput(
                format="%d.%m.%Y",
                attrs={
                    "class": (
                        "form-input "
                        "birth-date-input"
                    ),
                    "placeholder": "ДД.ММ.ГГГГ",
                    "autocomplete": "bday",
                },
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": (
                        "Например, Москва"
                    ),
                },
            ),
            "zodiac_sign": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": (
                        "Напишите немного о себе..."
                    ),
                    "rows": 5,
                },
            ),
            "notifications_enabled": (
                forms.CheckboxInput(
                    attrs={
                        "class": (
                            "notifications-checkbox"
                        ),
                    },
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
            "avatar"
        ].required = False

        self.fields[
            "timezone"
        ].required = False

        self.fields[
            "birth_date"
        ].input_formats = [
            "%d.%m.%Y",
            "%Y-%m-%d",
        ]

class RegisterForm(
    UserCreationForm,
):
    email = forms.EmailField(
        required=True,
        label="Электронная почта",
        help_text=(
            "Введите электронную почту. "
            "На неё придёт письмо для подтверждения."
        ),
        error_messages={
            "required": (
                "Введите электронную почту."
            ),
            "invalid": (
                "Введите корректный адрес "
                "электронной почты."
            ),
        },
    )

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "personal_data_consent",
            "terms_consent",
        )

        labels = {
            "username": "Логин",
        }

        help_texts = {
            "username": (
                "Введите логин для входа."
            ),
        }

        error_messages = {
            "username": {
                "required": (
                    "Введите логин."
                ),
                "unique": (
                    "Пользователь с таким именем "
                    "уже существует."
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
            },
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
            },
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

    personal_data_consent = forms.BooleanField(
        required=True,
        label="",
        error_messages={
            "required": (
                "Необходимо принять согласие "
                "на обработку персональных данных."
            ),
        },
    )

    terms_consent = forms.BooleanField(
        required=True,
        label="",
        error_messages={
            "required": (
                "Необходимо принять "
                "Пользовательское соглашение."
            ),
        },
    )

    def clean_username(self):
        username = (
            self.cleaned_data["username"]
            .strip()
        )

        if User.objects.filter(
            username__iexact=username,
        ).exists():
            raise forms.ValidationError(
                "Пользователь с таким логином "
                "уже существует.",
            )

        return username

    def clean_email(self):
        email = (
            self.cleaned_data["email"]
            .strip()
            .lower()
        )

        if User.objects.filter(
            email__iexact=email,
        ).exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной "
                "почтой уже существует.",
            )

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get(
            "password1",
        )
        password2 = self.cleaned_data.get(
            "password2",
        )

        if not password2:
            raise forms.ValidationError(
                "Повторите пароль.",
            )

        if password1 != password2:
            raise forms.ValidationError(
                "Пароли не совпадают.",
            )

        try:
            password_validation.validate_password(
                password2,
                self.instance,
            )
        except ValidationError as error:
            raise forms.ValidationError(
                error.messages,
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


class RussianSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": (
                    "Введите новый пароль"
                ),
                "autocomplete": "new-password",
            },
        ),
        help_text=(
            "Пароль должен содержать не менее "
            "8 символов."
        ),
        error_messages={
            "required": (
                "Введите новый пароль."
            ),
        },
    )

    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": (
                    "Повторите новый пароль"
                ),
                "autocomplete": "new-password",
            },
        ),
        help_text=(
            "Введите новый пароль ещё раз."
        ),
        error_messages={
            "required": (
                "Повторите новый пароль."
            ),
        },
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get(
            "new_password1",
        )
        password2 = self.cleaned_data.get(
            "new_password2",
        )

        if not password2:
            raise forms.ValidationError(
                "Повторите новый пароль.",
            )

        if password1 != password2:
            raise forms.ValidationError(
                "Пароли не совпадают.",
            )

        try:
            password_validation.validate_password(
                password2,
                self.user,
            )
        except ValidationError as error:
            translated_errors = []

            for message in error.messages:
                if message == (
                    "This password is entirely numeric."
                ):
                    translated_errors.append(
                        "Пароль не должен состоять "
                        "только из цифр.",
                    )
                elif message == (
                    "This password is too short. "
                    "It must contain at least 8 characters."
                ):
                    translated_errors.append(
                        "Пароль должен содержать не менее "
                        "8 символов.",
                    )
                elif message == (
                    "This password is too common."
                ):
                    translated_errors.append(
                        "Этот пароль слишком простой. "
                        "Придумайте более сложный пароль.",
                    )
                elif message == (
                    "The password is too similar "
                    "to the username."
                ):
                    translated_errors.append(
                        "Пароль слишком похож на логин.",
                    )
                else:
                    translated_errors.append(
                        "Пароль не соответствует требованиям "
                        "безопасности.",
                    )

            raise forms.ValidationError(
                translated_errors,
            )

        return password2

from django import forms

from .models import Profile


class BioForm(
    forms.ModelForm,
):
    class Meta:
        model = Profile

        fields = (
            "display_name",
            "gender",
            "avatar",
            "bio",
            "birth_date",
            "city",
            "zodiac_sign",
            "timezone",
        )

        labels = {
            "display_name": "Как вас зовут?",
            "gender": "Ваш пол",
            "avatar": "Фото профиля",
            "bio": "Расскажите о себе",
            "birth_date": "Дата рождения",
            "city": "Город",
            "zodiac_sign": "Знак зодиака",
            "timezone": "Часовой пояс",
        }

        help_texts = {
            "display_name": (
                "Это имя будут видеть другие пользователи."
            ),
            "bio": (
                "Несколько слов о себе — по желанию."
            ),
        }

        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например, Никита",
                    "autocomplete": "name",
                },
            ),
            "gender": forms.RadioSelect(
                attrs={
                    "class": "gender-options",
                },
            ),
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-file",
                    "accept": "image/*",
                },
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "placeholder": (
                        "Напишите немного о себе..."
                    ),
                    "rows": 5,
                },
            ),
            "birth_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-input",
                    "type": "date",
                },
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например, Москва",
                    "autocomplete": "address-level2",
                },
            ),
            "zodiac_sign": forms.Select(
                attrs={
                    "class": "form-select",
                },
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

        self.fields[
            "gender"
        ].empty_label = None