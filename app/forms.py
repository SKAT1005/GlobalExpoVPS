from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя в админке.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Определите поля, которые будут отображаться при создании нового пользователя.
        # UserCreationForm автоматически добавляет поля для пароля.
        # email является USERNAME_FIELD, поэтому он будет запрошен.
        fields = (
            "email", "name", "surname", "phone", "balance",
            "is_staff", "is_active",
            # 'servers' (ManyToManyField) обычно не добавляют в форму создания,
            # так как его удобнее управлять после создания пользователя.
            # 'date_joined' имеет default=timezone.now, поэтому не нужно добавлять.
        )

class CustomUserChangeForm(UserChangeForm):
    """
    Форма для изменения существующего пользователя в админке.
    """
    class Meta:
        model = CustomUser
        # Определите все поля, которые могут быть изменены.
        fields = (
            "email", "name", "surname", "phone", "balance", "servers",
            "reforce_password", "is_staff", "is_active", "date_joined",
        )
