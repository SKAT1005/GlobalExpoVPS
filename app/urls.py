from django.urls import path

from .views import *

urlpatterns = [
    path('', main_view, name='index'),
    path('about_us', about_us_view, name='about_us'),
    path('conditions', conditions_view, name='conditions'),
    path('contacts', contacts_view, name='contacts'),
    path('gpu_servers', gpu_servers_view, name='gpu_servers'),
    path('ofert', ofert_view, name='ofert'),
    path('privacy_policy', privacy_policy_view, name='privacy_policy'),
    path('servers', servers_view, name='servers'),
    path('logout', logout_view, name='logout'),
    path('password_recovery', password_recovery, name='password_recovery'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('configurator', ConfiguratorView.as_view(), name='configurator'),
    path('get_locations', get_serverspace_location, name='get_locations'),
    path('get_price', get_price, name='get_price'),
    path('code-verify', code_verify, name='code_verify'),
    path('topup_success', topup_success, name='topup_success'),
    path('payment/create/', PaymentCreateView.as_view(), name='create_payment'),
    path('payment/status/<str:payment_id>/', PaymentStatusView.as_view(), name='payment_status'),
    path('webhook/tbank/', TbankWebhookView.as_view(), name='tbank_webhook'),
    path('send_message_in_bot', send_message_in_bot, name='send_message_in_bot'),
    path('buy_server', buy_server, name='buy_server'),
    path('turn_off_server', turn_off_server, name='turn_off_server'),
    path('delite_server', delite_server, name='delite_server'),
    path('password_recovery', password_recovery, name='password_recovery'),
    path('email_verify', email_verify, name='email_verify')
]
