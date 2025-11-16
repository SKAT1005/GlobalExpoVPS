# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Импортируем UserAdmin как BaseUserAdmin для удобства
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели CustomUser.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Поля, отображаемые в списке пользователей
    list_display = (
        "email", "name", "surname", "balance", "is_staff", "is_active", "date_joined",
    )
    # Поля, по которым можно фильтровать список пользователей
    list_filter = (
        "is_staff", "is_active", "date_joined",
    )
    # Поля, по которым можно искать пользователей
    search_fields = (
        "email", "name", "surname", "phone",
    )
    # Сортировка по умолчанию
    ordering = (
        "email",
    )

    # Группировка полей при редактировании существующего пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}), # Поле email и стандартное поле пароля для смены
        ("Личная информация", {"fields": ("name", "surname", "phone", "balance", "reforce_password")}),
        ("Серверы", {"fields": ("servers",)}),
        ("Права доступа", {"fields": ("is_staff", "is_active",)}), # У вас нет is_superuser, groups, user_permissions
        ("Важные даты", {"fields": ("date_joined",)}),
    )

    # Группировка полей при создании нового пользователя
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "name", "surname", "phone", "balance",
                "is_staff", "is_active",
                "password", "password2", # Поля пароля для подтверждения при создании
            )
        }),
    )

    # Для поля ManyToMany 'servers' удобнее использовать фильтр
    filter_horizontal = ("servers",)

    # Отключаем возможность изменения `date_joined` и `last_login` (если бы оно было)
    # при редактировании, т.к. они устанавливаются автоматически.
    readonly_fields = ("date_joined",)


# Регистрируем модель CustomUser с вашим CustomUserAdmin классом
admin.site.register(CustomUser, CustomUserAdmin)
