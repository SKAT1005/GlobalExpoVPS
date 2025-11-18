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
    history = models.ManyToManyField('History', blank=True, verbose_name='История пополнения')
    collect_server = models.IntegerField(default=0, verbose_name='Сколько серверов собирается')

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
    pay_date = models.DateTimeField(verbose_name='Дата последней оплаты')


class Verify(models.Model):
    email = models.EmailField(verbose_name='Почта для верефикации')
    code = models.IntegerField(default=None, blank=True, null=True, verbose_name='Код для подтверждения почты')


class History(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата пополнения')
    amount = models.FloatField(verbose_name='Сумма пополнения')

    def format_amount(self):
        return f"{self.amount:,.2f}".replace(',', ' ')

    def format_datetime_russian(self):
        russian_month_names_genitive = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        dt_obj = self.date
        day = dt_obj.day
        month_name = russian_month_names_genitive[dt_obj.month]
        year = dt_obj.year
        hour = dt_obj.hour
        minute = dt_obj.minute
        return f"{day} {month_name} {year}, {hour:02}:{minute:02}"