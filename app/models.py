from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields) # Используйте normalized_email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Обычно суперпользователь активен

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin): # Изменено на AbstractBaseUser и PermissionsMixin
    name = models.CharField(max_length=128, verbose_name='Имя клиента')
    surname = models.CharField(max_length=128, verbose_name='Фамилия клиента')
    email = models.EmailField(unique=True, verbose_name="Email адрес")
    phone = models.CharField(max_length=32, blank=True, null=True, verbose_name='Номер телефона')
    balance = models.FloatField(default=0, verbose_name="Баланс пользователя")
    servers = models.ManyToManyField('Server', blank=True, verbose_name='Серверы пользователя')
    reforce_password = models.IntegerField(default=None, blank=True, null=True, verbose_name='Точка для восстановления пароля')

    # Добавляем поля, которые обычно есть в AbstractUser, но отсутствуют в AbstractBaseUser
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала') # Для доступа к админке
    is_active = models.BooleanField(default=True, verbose_name='Активен') # Может ли пользователь войти
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Дата регистрации')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # email уже является USERNAME_FIELD, поэтому здесь ничего не нужно

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self): # Изменено на __str__
        return self.email

    # Методы, которые AbstractUser предоставляет по умолчанию, если вам нужны
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def update_balance(self, amount):
        self.balance += amount
        self.save(update_fields=['balance'])


class Server(models.Model):
    server_id = models.CharField(max_length=128, verbose_name='ID сервера')
    price = models.FloatField(verbose_name='Цена сервера')
    buy_date = models.DateTimeField(verbose_name='Дата покупки/продления сервера')