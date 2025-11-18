import base64
import datetime
import ipaddress
import json
import math
import random
import threading
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from GlobalExpoVPS.settings import EMAIL_HOST_USER
from app.models import CustomUser, Server, Verify, History
from app.tbank_methods import create_tbank_payment, get_payment_status
import telebot

api_key = '0658bb976cf550df03209d4b465b0a85c25eaa0010564495f7fa75b18b938036'
bot = telebot.TeleBot('7071542790:AAHawETvNXlXppKYzAhd9tShU1GN9ja81Vo')
CHAT_ID = -5063638309
headers = {
    'X-API-KEY': api_key
}

locationNames = {
    'ix1': 'Москва, 2nd Gen Intel',
    'ds1': 'Москва, 5th Gen Intel',
    'kz': 'Алматы',
    'uae': 'Дубай',
    'am2': 'Амстердам',
    'ca': 'Торонто',
    'nj3': 'Нью-Джерси',
    'br': 'Сан-Паулу'
}

# Глобальное хранилище метаданных платежей
PAYMENT_METADATA = {}  # payment_id → { "callback_url": ..., "user_id": ... }


@csrf_exempt
def feedback(request):
    pass


def main_view(request):
    if request.method == 'GET':
        return render(request, 'index.html')


def about_us_view(request):
    if request.method == 'GET':
        return render(request, 'about_us.html')


def conditions_view(request):
    if request.method == 'GET':
        return render(request, 'conditions.html')


def contacts_view(request):
    if request.method == 'GET':
        return render(request, 'contacts.html')


def gpu_servers_view(request):
    if request.method == 'GET':
        return render(request, 'gpu_servers.html')


def ofert_view(request):
    if request.method == 'GET':
        return render(request, 'ofert.html')


def privacy_policy_view(request):
    if request.method == 'GET':
        return render(request, 'privacy_policy.html')


def servers_view(request):
    if request.method == 'GET':
        return render(request, 'servers.html')


def topup_success(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            amount = int(data.get('amount'))
            history = History.objects.create(amount=amount)
            user.balance += amount
            user.save(update_fields=['balance'])
            user.history.add(history)
            return JsonResponse({'status': 'complite'}, status=200)


def email_verify(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            code = random.randint(100000, 999999)
            subject = 'Подтверждение почты'
            html_message = render_to_string('verify_email.html', {
                'code': code
            })

            # Текстовая версия (для клиентов без поддержки HTML)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            verify, _ = Verify.objects.get_or_create(
                email=email
            )
            verify.code = code
            verify.save()
            return JsonResponse({'status': 'complite'}, status=200)
        else:
            return JsonResponse({'status': 'faild'}, status=400)
    except Exception:
        return JsonResponse({'status': 'faild'}, status=400)


def password_recovery(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            code = random.randint(100000, 999999)
            subject = 'Восстановление пароля'

            user.reforce_password = code
            user.save(update_fields=['reforce_password'])
            html_message = render_to_string('recovery_email.html', {
                'code': code
            })

            # Текстовая версия (для клиентов без поддержки HTML)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            return JsonResponse({'status': 'complite'}, status=200)
        else:
            return JsonResponse({'status': 'faild'}, status=400)


def code_verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        user = CustomUser.objects.filter(email=email, reforce_password=code).first()
        if user:
            return JsonResponse({'status': 'complite'}, status=200)
    return JsonResponse({'status': 'faild'}, status=400)


class ProfileView(View):

    def get(self, request):
        user = request.user
        user_servers = []
        if user.is_authenticated:
            get_servers_url = 'https://api.serverspace.ru/api/v1/servers'
            responce = requests.get(url=get_servers_url, headers=headers).json()
            for server in responce['servers']:
                server_id = server['id']
                if user.servers.filter(server_id=server_id):
                    server['ram_mb'] //= 1024
                    server['volumes'][0]['size_mb'] //= 1024
                    server['location_id'] = locationNames[server['location_id']]
                    user_servers.append(server)
        return render(request, 'profile.html', context={'servers': user_servers, 'registration': False})

    def post(self, request):
        errors = []
        registration = False
        if 'login' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                user.reforce_password = None
                user.save(update_fields=['reforce_password'])
                login(request, user)
            else:
                errors.append('Неверный email или пароль.')
        elif 'registration' in request.POST:
            registration = True
            email = request.POST.get('email')
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            code = request.POST.get('code')
            try:
                Verify.objects.get(email=email, code=int(code))
            except Exception:
                errors.append('Введен неверный код')

            # Словарь для хранения ошибок, которые будут переданы в шаблон
            try:
                validate_email(email)  # Проверяем формат email
            except ValidationError:
                errors.append("Введите корректный email адрес.")

            if not errors:  # Если формат верен, проверяем на уникальность
                if CustomUser.objects.filter(email=email).exists():
                    errors.append("Пользователь с таким email уже существует.")
            if not errors:
                try:
                    user = CustomUser.objects.create_user(email=email, password=password, name=name, surname=surname,
                                                          phone=phone)

                    login(request, user)

                except IntegrityError:
                    errors.append("email уже занят")
                except Exception as e:
                    # Общая обработка других возможных ошибок
                    errors.append(f"Произошла непредвиденная ошибка: {e}")
        elif 'recovery_password' in request.POST:
            password = request.POST.get('password')
            email = request.POST.get('email')
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()
            user = authenticate(request, email=email, password=password)
            if user is not None:
                user.reforce_password = None
                user.save(update_fields=['reforce_password'])
                login(request, user)
            else:
                errors.append('Неверный email или пароль.')
        context = {'errors': errors, 'registration': registration}
        return render(request, 'profile.html', context=context)


def logout_view(request):
    logout(request)
    return redirect('profile')


class ConfiguratorView(View):
    def get(self, request):
        return render(request, 'configurator.html')


@csrf_exempt
def get_serverspace_location(request):
    url = 'https://api.serverspace.ru/api/v1/locations'
    data = requests.get(url=url, headers=headers).json()

    return JsonResponse(data, safe=False)


@csrf_exempt
def send_message_in_bot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        text = f'Новая заявка:\n' \
               f'Имя клиента: {name}\n' \
               f'Почта для связи: {email}\n' \
               f'Телефон для связи: {phone}\n' \
               f'Текст сообщений:\n' \
               f'{message}'
        bot.send_message(chat_id=CHAT_ID, text=text)
        return HttpResponse(status=200)


def turn_off_server(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        server_id = data.get('server_id')
        action = data.get('action')
        turn_off = f'https://api.serverspace.ru/api/v1/servers/{server_id}/power/shutdown'
        turn_on = f'https://api.serverspace.ru/api/v1/servers/{server_id}/power/on'
        if action == 'on' and request.user.servers.filter(server_id=server_id):
            requests.post(url=turn_on, headers=headers)
        elif action == 'off' and request.user.servers.filter(server_id=server_id):
            requests.post(url=turn_off, headers=headers)
        return HttpResponse("OK")
    return HttpResponseBadRequest(status=404)


def delite_server(request):
    try:
        if request.method == 'DELETE' and request.user.is_authenticated:
            data = json.loads(request.body)
            server_id = data.get('server_id')
            user = request.user
            server = user.servers.filter(server_id=server_id).first()
            if server:
                delete_url = f'https://api.serverspace.ru/api/v1/servers/{server_id}'
                requests.delete(url=delete_url, headers=headers)
                server.delete()
            return HttpResponse("OK")
        return HttpResponseBadRequest(status=404)
    except Exception:
        return HttpResponseBadRequest(status=404)


@csrf_exempt
def get_price(request):
    data = json.loads(request.body)
    url = 'https://api.serverspace.ru/api/v1/servers/price'
    responce = requests.post(url=url, json=data, headers=headers).json()
    try:
        responce['price'] *= 1.1
        return JsonResponse(responce, safe=False)
    except Exception:
        return HttpResponseBadRequest(status=400)


def get_server_id(task_id, price, user):
    get_task_url = f'https://api.serverspace.ru/api/v1/tasks/{task_id}'
    user.collect_server += 1
    user.save(update_fields=['collect_server'])
    while True:
        try:
            responce = requests.get(url=get_task_url, headers=headers).json()
            server_id = responce['task']['server_id']
            server = Server.objects.create(
                server_id=server_id,
                price=price,
                buy_date=timezone.now(),
                pay_date=timezone.now()
            )
            user.servers.add(server)
            user.collect_server -= 1
            user.save(update_fields=['collect_server'])
            break
        except KeyError:
            time.sleep(5)


@csrf_exempt
def buy_server(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            url = 'https://api.serverspace.ru/api/v1/servers/price'
            responce = requests.post(url=url, json=data, headers=headers).json()
            try:
                price = responce['price'] * 1.1
                pay = round(price / 720, 2)
                new_balance = round(user.balance - pay, 2)
                if new_balance < 0:
                    return HttpResponseBadRequest(status=402)
                try:
                    buy_server_url = 'https://api.serverspace.ru/api/v1/servers'
                    data['networks'] = [{"bandwidth_mbps": 50}]
                    email = 'slavatukin@mail.ru'
                    number = str(int(time.time()))
                    new_string = f'{email}_{number}'
                    server_name = base64.b64encode(new_string.encode('utf-8')).decode('utf-8')[:-1]
                    data['name'] = server_name
                    data['server_init_script'] = 'sudo apt update'
                    responce = requests.post(url=buy_server_url, json=data, headers=headers).json()
                    time.sleep(3)
                    user.balance = new_balance
                    user.save(update_fields=['balance'])
                    task_id = responce['task_id']
                    thread = threading.Thread(target=get_server_id, args=(task_id, price, user))
                    thread.start()
                    return HttpResponse("OK")
                except Exception as e:
                    print(f'Error: {e}')
                    return HttpResponseBadRequest(status=404)
            except Exception:
                return HttpResponseBadRequest(status=400)
        except Exception as e:
            print(f'Error: {e}')
            return HttpResponseBadRequest(status=404)
    return render(request, 'about_us.html')


class PaymentCreateView(View):
    def post(self, request):
        try:
            # Парсим JSON данные из запроса
            body = json.loads(request.body)
            amount = body.get('amount')
            callback_url = body.get('callback_url')
            user_id = body.get('user_id')

            # Валидация обязательных полей
            if not amount or not callback_url:
                return JsonResponse(
                    {"error": "Обязательные поля: amount, callback_url"},
                    status=400
                )

            payment = create_tbank_payment(amount)
            payment_id = payment.get('PaymentId')

            PAYMENT_METADATA[payment_id] = {
                "callback_url": callback_url,
                "user_id": user_id  # может быть None
            }

            return JsonResponse({
                "id": payment_id,
                "confirmation_url": payment.get('PaymentURL'),
                "description": payment.get('Description')
            })

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Невалидный JSON"},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Ошибка при создании платежа: {str(e)}"},
                status=500
            )


class PaymentStatusView(View):
    def get(self, request, payment_id):
        try:
            status_result = get_payment_status(payment_id)
            return JsonResponse({"status": status_result})
        except Exception as e:
            return JsonResponse(
                {"error": f"Платёж не найден: {str(e)}"},
                status=404
            )


def verify_tbank_ip(client_ip: str) -> bool:
    trusted_networks = [
        "91.194.226.0/23",
        "91.218.132.0/24",
        "91.218.133.0/24",
        "91.218.134.0/24",
        "91.218.135.0/24",
        "212.49.24.0/24",
        "212.233.80.0/24",
        "212.233.81.0/24",
        "212.233.82.0/24",
        "212.233.83.0/24",
    ]

    try:
        ip_obj = ipaddress.ip_address(client_ip)
    except ValueError:
        return False  # Некорректный IP

    for network in trusted_networks:
        if ip_obj in ipaddress.ip_network(network):
            return True

    return False


@method_decorator(csrf_exempt, name='dispatch')
class TbankWebhookView(View):
    def post(self, request):
        client_ip = self.get_client_ip(request)

        if not verify_tbank_ip(client_ip):
            return HttpResponse("Forbidden: IP not allowed", status=403)

        try:
            body = request.body.decode('utf-8')
            event = json.loads(body)
        except Exception:
            return HttpResponse("Invalid JSON", status=400)

        if event.get("Status") != "CONFIRMED":
            return HttpResponse("OK")

        payment_id = str(event.get("PaymentId"))

        metadata = PAYMENT_METADATA.get(payment_id)
        if not metadata:
            return HttpResponse("OK")

        callback_url = metadata.get("callback_url")
        user_id = metadata.get("user_id")

        # Обновление баланса в Firebase, если user_id указан
        if user_id:
            try:
                amount = int(event.get("Amount")) // 100

                user = CustomUser.objects.filter(id=user_id).first()

                if user:
                    user.balance += amount
                    user.save(update_fields=['balance'])
            except Exception as e:
                pass

        return HttpResponse("OK")

    def get_client_ip(self, request):
        """Получение реального IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def update_server_price():
    while True:
        thirty_days_ago = timezone.now() - datetime.timedelta(hours=1)
        for server in Server.objects.filter(pay_date__lt=thirty_days_ago):
            user = CustomUser.objects.filter(servers=server).first()
            pay = round(server.price / 720, 2)
            if user.balance >= pay:
                new_balance = round(user.balance - pay, 2)
                server.pay_date = timezone.now()
                server.save(update_fields=['pay_date'])
                user.balance = new_balance
                user.save(update_fields=['balance'])
            else:
                server_id = server.server_id
                delete_url = f'https://api.serverspace.ru/api/v1/servers/{server_id}'
                requests.delete(url=delete_url, headers=headers)
                server.delete()
        time.sleep(60 * 10)


polling_thread2 = threading.Thread(target=update_server_price)
polling_thread2.start()
