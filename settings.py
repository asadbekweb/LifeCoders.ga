#!/usr/bin/env python
# -*- coding: utf-8 -*-


db_url='sqlite:///db.sqlite'

ref_pay_perc_1lvl=0 #столько получит от 1 уровная рефералов за оплату
ref_pay_perc_2lvl=0 #столько получит от 2 уровная рефералов за оплату
ref_view_pay_1lvl=0.80 #столько получит от 1 уровная рефералов за подписку
ref_view_pay_2lvl=0 #столько получит от 2 уровная рефералов за подписку
user_view_perc=0.40 #столько получит пользователь за вступление(проценты от стоимости установленной заказчиком)
min_out_pay=20 #минимальная сумма для вывода
min_post_cost=0.20 #минимальная стоимость 1 подписчика

number=998933061110
qiwi_token='6e02ac33af42f2d34e3bd9c8b5573067'

ya_number=3333
ya_token=''

telegram_token='692792333:AAF40LfPVe14iof_tMEax9vCIpDIkZWdcI4'


uah_to_rub=2.16
usd_to_rub=70.85
eur_to_rub=72.73

admins = [370436629,409538530]

tutorial_url = 'http://telegra.ph/'





WEBHOOK_HOST = '85.143.175.216'
WEBHOOK_PORT = 443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)

WEBHOOK_URL_PATH = "/{}/".format(telegram_token)
