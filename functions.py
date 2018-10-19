#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telebot import types
import ast
import messages
import settings
import time
import qiwi
from random import  randint
from time import sleep
from yandex_money import api
wallet = api.Wallet(access_token=settings.ya_token)

class obj(object):
    def __init__(self, d):
        for a, b in list(d.items()):
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)
class AnswFunctions(object):
    def __init__(self,tb,db):
        self.tb = tb

        self.db = db

        self.me =  tb.get_me()
    def mailer(self,message):
        users = self.db.get.users(_limit=99999)
        users = [users[x:x + 30] for x in range(0, len(users), 30)]

        print ('mail to {}'.format(len(users * 30)))
        for iu in users:
            for us in iu:
                try:
                    if message.photo is not None:
                        self.tb.send_photo(chat_id=us['user_id'], photo=message.photo[-1].file_id,caption=message.caption)
                    elif message.text is not None:
                        self.tb.send_message(chat_id=us['user_id'], text=message.text)
                    elif message.audio is not None:
                        self.tb.send_audio(chat_id=us['user_id'], audio=message.audio.file_id,caption=message.caption)
                    elif message.voice is not None:
                        self.tb.send_voice(chat_id=us['user_id'], voice=message.voice.file_id,caption=message.caption,duration=message.voice.duration)
                    elif message.document is not None:
                        self.tb.send_document(chat_id=us['user_id'], data=message.document.file_id,caption=message.caption)
                except Exception as exp:

                    if 'chat not found' in str(exp.args):
                        continue
                    else:
                        print(exp.args)
                        continue



            time.sleep(2)




    def gen_code(self,user,send_message,message):
        codes = self.db.get.code_to_qiwi(user=user['user_id'])
        if len(codes)>0:
            send_message(message,messages.balance['code'])
            return send_message(message,{'text':codes[0]['code'],'markup':messages.start['markup']})
        else:
            rand_code = randint(1000,99999)
            self.db.insert.code_to_qiwi(user=user['user_id'],code=str(rand_code),chat_id=user['user_id'])
            send_message(message,messages.balance['code'])
            send_message(message,{'text':str(rand_code),'markup':messages.start['markup']})
            return



    def gen_code_ya(self,user,send_message,message):
        codes = self.db.get.code_to_qiwi(user=user['user_id'])
        if len(codes)>0:
            send_message(message,messages.balance['ya'],parse_mode='Markdown',disable_web_page_preview=True)
            return send_message(message,{'text':codes[0]['code'],'markup':messages.start['markup']},disable_web_page_preview=True)
        else:
            rand_code = randint(1000,99999)
            self.db.insert.code_to_qiwi(user=user['user_id'],code=str(rand_code),chat_id=user['user_id'])
            send_message(message,messages.balance['ya'],parse_mode='Markdown',disable_web_page_preview=True)
            send_message(message,{'text':str(rand_code),'markup':messages.start['markup']})
            return
    def check_qiwi(self,send_message):
        while True:

            history = qiwi.get_history(rows=50,operation='IN')

            if history:
                for op in history['data']:
                    if op['status'] == "SUCCESS":
                        # self.db.insert.qiwi(trans_id=op['txnId'],user_id=op['account'],type=op['type'],date=op["date"],currency=op['sum']['currency'],count=op['sum']['amount'],comment=op['comment'])
                        if op['comment']==None:
                            code = self.db.get.code_to_qiwi(code='kex')
                        else:
                            code = self.db.get.code_to_qiwi(code=op['comment'])
                        if len(code)>0:
                            user = self.db.get.users(user_id=code[0]['user'])
                            if len(user)>0:
                                user = user[0]
                                if op['sum']['currency'] == 643:
                                    count = op['sum']['amount']
                                elif op['sum']['currency'] == 980:
                                    count = op['sum']['amount']*settings.uah_to_rub
                                elif op['sum']['currency'] == 840:
                                    count = op['sum']['amount']*settings.usd_to_rub
                                elif op['sum']['currency'] == 978:
                                    count = op['sum']['amount']*settings.eur_to_rub
                                else:
                                    count = op['sum']['amount']
                                mem = {}
                                mem.update(messages.balance['success'])
                                mem['text'] = mem['text'].format(count)
                                send_message(obj({'chat': {'id': code[0]['user']},'from_user':{'id':user['user_id']}}), mem)
                                self.balance(type='pay_in',user=user,count=count)



                                self.db.delete.code_to_qiwi(user=user['user_id'])
            time.sleep(20)



    def check_ya(self,send_message):
        while True:

            history = wallet.operation_history({'type':'deposition','details':'true'})

            for op in history['operations']:

                if op['status'] == "success":
                    if 'message' in op:
                        code = op['message']
                    elif 'comment' in op:
                        code = op['comment']
                    elif 'details' in op:
                        code = op['details']
                    elif 'title' in op:
                        code = op['title']
                    else:
                        code =''
                    if 'sender' in op:
                        sender = op['sender']
                    else:
                        sender = ''
                    # self.db.insert.qiwi(trans_id=op['operation_id'],user_id=sender,type='ya',date=op["datetime"],currency=683,count=op['amount'],comment=code)
                    count = op['amount']
                    self.check_code(code=code, count=count, send_message=send_message, number=sender)
                    user_code = self.db.get.code_to_qiwi(code=code)



            time.sleep(20)





    def check_code(self,code,count,send_message,number):
        code = self.db.get.code_to_qiwi(code=code)
        if len(code)>0:
            user = self.db.get.users(user_id=code[0]['user'])
            if len(user)<1:
                return
            self.balance(type='pay_in', user=user[0], count=count)
            mem = {}
            mem.update(messages.balance['success'])
            mem['text'] = '''💥 Ваш счёт пополнен на {} рублей.
💎Ваш баланс: {} рублей'''.format(count,round(user[0]['balance']+count))
            send_message(obj({'chat': {'id': code[0]['user']},'from_user':{'id':user[0]['user_id']}}), mem)

            self.db.delete.code_to_qiwi(user=user[0]['user_id'])
        else:
            pass

    def gen(self,rows):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if rows == 'remove':
            return types.ReplyKeyboardRemove()

        for r in rows:
            markup.row(*[types.KeyboardButton(i,request_contact=True) if 'Отправить номер вашего телефона' in i else types.KeyboardButton(i)  for i in r])
        return markup

    def gen_inl(self,rows):
        markup = types.InlineKeyboardMarkup()

        if rows == 'remove':
            return types.ReplyKeyboardRemove()

        for r in rows:

            markup.add(*[types.InlineKeyboardButton(text=i['text'],callback_data=i['data']) if 'url' not in i else types.InlineKeyboardButton(text=i['text'],url=i['url'])   for i in r])
        return markup

    def sub(self,user,send_message,message):
        try:
            user_channels=ast.literal_eval(user['channels'])
        except:
            user_channels=[]
        try:
            add_info = ast.literal_eval(user['add_info'])
            user_last_channel=add_info['last_channel']
        except:
            add_info={}
            user_last_channel=""
        channels = self.db.get.channels(order_by='-cost',_limit=999)
        for p in channels:
            try:
                if p['channel_name'] == user_last_channel:
                    continue
            except:
                continue
            user_c = self.chechk_admin(p['channel_name'],self.me.username)

            if not user_c:
                self.db.delete.channels(channel_name=p['channel_name'])
                continue


            channel_name = p['channel_name']
            if p['views'] < 1:

                self.db.delete.channels(channel_name=p['channel_name'])
                self.tb.send_message(p['user_id'],text='''📣Уважаемый рекламодатель!
🔝Ваш заказ выполнен, все заказанные люди подписались на канал {}!'''.format(p['channel_name']))
                continue
            if channel_name not in user_channels:



                mes_id = self.tb.send_message(chat_id=message.chat.id,text='Подпишись на этот канал и вернись чтобы получить вознаграждение!',reply_markup=self.gen_inl([[{'text':'Перейти к каналу','url':'https://t.me/{}'.format(p['channel_name'].replace('@',''))}],[{'text':'Проверить подписку','data':'chck-public-{}'.format(p['channel_name'].replace('@',''))}]]))

                # end_mes = {}
                # end_mes.update(messages.view_end)
                # end_mes['text']+='{}p'.format(p['cost']*settings.user_view_perc)
                # sleep(3)
                # self.tb.delete_message(chat_id=message.from_user.id,message_id=mes_id.message_id)
                # self.tb.send_message(message.chat.id, text='Чтобы забрать награду - нажми кнопку ниже:', reply_markup=self.gen_inl([[{'text':'Перейти к каналу','url':'https://t.me/{}'.format(p['channel_name'].replace('@',''))}],[{'text':'Проверить подписку','data':'chck-public-{}'.format(p['channel_name'].replace('@',''))}]]))
                # user_channels.append(channel_name)
                # self.balance(type='view_pay',count=p['cost']*settings.user_view_perc,user=user)
                add_info.update({'last_channel':p['channel_name']})
                self.db.insert.users(user_id=user['user_id'],add_info=str(add_info))
                # self.db.insert.posts(post_id=p['post_id'],views=p['views']-1)
                return

            else:
                continue
        send_message(message, messages.sub_err)
        return

    def check_sub(self,channel,user,send_message,message):
        user_channels = ast.literal_eval(user['channels'])
        try:
            channel='@'+channel.replace('@','')
            user_channels = ast.literal_eval(user['channels'])
            try:
                channels = self.db.get.channels(channel_name=channel)[0]
            except:
                return False
            user_c = self.tb.get_chat_member(chat_id=channel,user_id=+user['user_id'])
            if user_c.status =='member' and channel not in user_channels:
                user_channels.append(channel)
                succ_text = {}
                succ_text.update(messages.view_end)
                succ_text['text']=succ_text['text'].format(round(channels['cost'] * settings.user_view_perc,2),round(user['balance']+channels['cost'] * settings.user_view_perc,2))
                self.tb.delete_message(chat_id=message.chat.id,message_id=message.message_id)
                send_message(message,succ_text)
                self.db.insert.users(user_id=user['user_id'],channels=str(user_channels))
                sleep(0.2)
                self.db.insert.channels(channel_name=channel,views=channels['views']-1)
                self.balance(type='view_pay', count=channels['cost'] * settings.user_view_perc, user=user)
                return True
            elif channel in user_channels:
                try:
                    self.tb.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                          text='Вы уже получили награду!')
                except:
                    pass
            else:

                self.tb.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text='Вы все еще не подписаны!',reply_markup=self.gen_inl([[{'text':'Перейти к каналу','url':'https://t.me/{}'.format(channel.replace('@',''))}],[{'text':'Проверить подписку','data':'chck-public-{}'.format(channel)}]]))
                return False
        except:
            user_channels.append(channel)
            self.db.insert.users(user_id=user['user_id'], channels=str(user_channels))
            self.tb.send_message(message.chat.id,text='Возникла ошибка! Попробуйте другой канал')


    def chechk_admin(self,channel,username):
        try:
            admins = self.tb.get_chat_administrators(chat_id=channel)
            for i in admins:
                if i.user.username==username:
                    return True
                return False
        except:
            return False


    def post_confirm(self,user,send_message,message):
        add_info = ast.literal_eval(user['add_info'])
        if self.balance(type='pay_post',user=user,count=add_info['count']*add_info['cost']):
            self.db.insert.channels(channel_name=add_info['channel_name'],channel_id=add_info['channel_id'],active=True,views=add_info['count'],cost=add_info['cost'],user_id=user['user_id'])
            return send_message(message,messages.for_advert['success_done'])
        else:
            return send_message(message,messages.for_advert['error_money'])

    # todo все транзакции в отдельную дб, рефералы второго уровня, изменение баланса через админку
    def balance(self,type,user,count,qiwi_number='',username='',out_type='QIWI'):
        while True:
            trans_id =randint(0, 9999999999)
            trans = self.db.get.transactions(trans_id=trans_id)
            if len(trans)>0:
                continue
            else:
                break
        username = user['username']
        if type=='pay_in':
            if user['ref_pay'] != None:
                ref_balance = user['ref_pay']
            else:
                ref_balance = 0
            pre_balance=user['balance']
            referal = user['referal']

            self.db.insert.transactions(trans_id=trans_id, count=count, type='pay_in',
                                        user_id=user['user_id'], date=time.strftime("%d/%m/%Y"))
            if referal != 0:
                ref1st = self.db.get.users(user_id=referal)
                if len(ref1st) > 0:
                    ref_balance = ref_balance + (count * settings.ref_pay_perc_1lvl)
                    self.db.insert.users(user_id=referal,
                                         ref_balance=ref1st[0]['ref_balance'] + count * settings.ref_pay_perc_1lvl,ref_pay=ref1st[0]['ref_pay'] + count * settings.ref_pay_perc_1lvl)
                    ref2st = self.db.get.users(user_id=ref1st[0]['referal'])
                    if len(ref2st) > 0:
                        ref_balance = ref_balance + (count * settings.ref_pay_perc_2lvl)
                        self.db.insert.users(user_id=ref1st[0]['referal'],
                                             ref_balance=ref2st[0]['ref_balance'] + count * settings.ref_pay_perc_2lvl,ref_pay=ref2st[0]['ref_pay'] + count * settings.ref_pay_perc_2lvl)

            self.db.insert.users(user_id=user['user_id'], balance=pre_balance + count)
            return True
# todo Пользователь будет получать 40 процентов от стоимости поста, реферер 1 Уровня  10, а второго 5
        if type=='view_pay':
            if user['ref_pay'] != None:
                ref_balance = user['ref_pay']
            else:
                ref_balance = 0
            pre_balance=user['balance']
            referal = user['referal']
            self.db.insert.transactions(trans_id=trans_id,count=count,type='view_pay',user_id=user['user_id'],date=time.strftime("%d/%m/%Y"))
            if referal != 0:
                ref1st = self.db.get.users(user_id=referal)
                if len(ref1st) > 0:
                    ref_balance=ref_balance+count * settings.ref_view_pay_1lvl
                    self.db.insert.users(user_id=referal,
                                         ref_balance=ref1st[0]['ref_balance'] + count * settings.ref_view_pay_1lvl,ref_pay=ref1st[0]['ref_pay'] + count * settings.ref_view_pay_1lvl)
                    ref2st = self.db.get.users(user_id=ref1st[0]['referal'])
                    if len(ref2st) > 0:
                        ref_balance = ref_balance + count * settings.ref_view_pay_2lvl
                        self.db.insert.users(user_id=ref1st[0]['referal'],
                                             ref_balance=ref2st[0]['ref_balance'] + count * settings.ref_view_pay_2lvl,ref_pay=ref2st[0]['ref_pay'] + count * settings.ref_view_pay_2lvl)

            self.db.insert.users(user_id=user['user_id'], balance=pre_balance + count)

            return True


        if type=='pay_post':
            try:
                pre_balance=user['balance']
                if count <= pre_balance:
                    balance = pre_balance-count
                    self.db.insert.users(user_id=user['user_id'],balance=balance)
                    sleep(0.2)
                    self.db.insert.transactions(trans_id=trans_id, count=count, type='pay_post',
                                                user_id=user['user_id'], date=time.strftime("%d/%m/%Y"))
                    return True
                elif count <= pre_balance+user['ref_balance']:
                    minus_ref = pre_balance+user['ref_balance']-count
                    ref_balance = user['ref_balance']
                    self.db.insert.users(user_id=user['user_id'],balance=minus_ref,ref_balance=0)
                    sleep(0.2)
                    self.db.insert.transactions(trans_id=trans_id, count=count, type='pay_post',
                                                user_id=user['user_id'], date=time.strftime("%d/%m/%Y"))
                    return True
                else:
                    return False
            except:
                return False

        if type=='pay_out':
            try:
                pre_balance=user['balance']
                if count <= pre_balance:
                    balance = pre_balance-count
                    self.db.insert.users(user_id=user['user_id'],balance=balance)
                    sleep(0.2)
                    self.db.insert.transactions(trans_id=trans_id, count=count, type='pay_out',
                                                user_id=user['user_id'], date=time.strftime("%d/%m/%Y"),status='pending',qiwi_number=qiwi_number,username=username,menu=out_type)
                    return True
                elif count <= pre_balance+user['ref_balance']:
                    minus_ref = pre_balance + user['ref_balance'] - count
                    ref_balance = user['ref_balance']
                    self.db.insert.users(user_id=user['user_id'],balance=minus_ref,ref_balance=0)
                    sleep(0.2)
                    self.db.insert.transactions(trans_id=trans_id, count=count, type='pay_out',
                                                user_id=user['user_id'], date=time.strftime("%d/%m/%Y"),status='pending',qiwi_number=qiwi_number,username=username,menu=out_type)
                    return True
                else:
                    return False
            except:
                return False

    def inline_requests(self,page_n):
        pages = 6
        btns = []
        requests = self.db.get.transactions(type='pay_out',status='pending')
        requests= [requests[x:x+5] for x in range(0, len(requests),5)]
        last = False
        if len(requests)<1:
            return self.gen_inl([[{'text':'0','data':'Null'}]])
        else:
            if len(requests)==1:

                for i in requests[0]:
                    btns.append([{'text':'@{} - {}p {}'.format(i['username'],i['count'],i['menu']),'data':'tid_'+str(i['trans_id'])}])

                return self.gen_inl(btns)
            else:
                for i in requests[page_n-1]:
                    btns.append([
                        {'text': '@{} - {}p'.format(i['username'], i['count']), 'data': 'tid_' + str(i['trans_id'])}])
                if len(requests)>page_n and page_n > 1:
                    btns.append([{'text':'< {}'.format(page_n-1),'data':'pgn_{}'.format(page_n-1)},{'text':'{}'.format(page_n),'data':'null'},{'text':'{} >'.format(page_n+1),'data':'pgn_{}'.format(page_n+1)}])
                elif page_n==1:
                    btns.append([{'text':' ','data':'null'},{'text':'{}'.format(page_n),'data':'null'},{'text':'{} >'.format(page_n+1),'data':'pgn_{}'.format(page_n+1)}])
                elif page_n==len(requests):
                    btns.append([{'text':'< {}'.format(page_n-1),'data':'pgn_{}'.format(page_n-1)},{'text':'{}'.format(page_n),'data':'null'},{'text':' '.format(page_n+1),'data':'null'.format(page_n+1)}])

                return self.gen_inl(btns)

class helpers(object):
    def new_referal(self,db,ref_id,own_id):
        owner = db.get.users(user_id=own_id)
        if len(owner)>0:
            refs = ast.literal_eval(owner[0]['refs'])
            refs.append(ref_id)
            db.insert.users(user_id=own_id,refs=str(refs))
            sleep(0.2)
            db.insert.users(user_id=ref_id,referal=own_id)
            return True
        else:
            return False

    def ifloat(self,string):
        try:
            return float(string)
        except:
            return False

    def ifint(self,string):
        try:
            return int(string)
        except:
            return False
