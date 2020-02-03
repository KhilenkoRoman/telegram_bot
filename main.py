import os
import telebot
import db
import datetime
import requests
import json
import re

KEY = os.environ.get('TELEGRAM_KEY')
TIME_THRESHOLD = datetime.datetime.now() - datetime.timedelta(days=7)

bot = telebot.TeleBot(KEY)
db.settup()


@bot.message_handler(commands=['list', 'lst'])
def list_rates(message):
    data = db.get_request('list', TIME_THRESHOLD)
    if not data:
        r = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
        if not r.status_code == 200:
            bot.send_message(message, "Excange api connection error")
            return
        data = r.text
        db.write('list', data, datetime.datetime.now())

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        bot.send_message(message, "Response decode error")
        return

    if data.get('rates'):
        reply = ''.join('- {}: {:8.2f}\n'.format(k, v) for k, v in data.get('rates').items() if k != "USD")
        bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=['exchange'])
def exchange_rate(message):
    request = message.text
    res = re.search(r'/exchange ((\$([0-9]+))|(([0-9]+) USD)) to ([A-Z]{3})$', request)
    if not res:
        bot.send_message(message.chat.id, "Wrong format\nEX: /exchange $10 to CAD or /exchange 10 USD to CAD")
        return
    value, currency = float(res.group(3) if res.group(3) else res.group(5)), res.group(6)

    data = db.get_request(currency, TIME_THRESHOLD)
    if not data:
        r = requests.get('https://api.exchangeratesapi.io/latest?base=USD&symbols={}'.format(currency))
        if r.status_code == 400:
            bot.send_message(message.chat.id, "No such currency")
            return
        elif not r.status_code == 200:
            bot.send_message(message.chat.id, "Excange api connection error")
            return
        data = r.text
        db.write(currency, data, datetime.datetime.now())

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        bot.reply_to(message.chat.id, "Response decode error")
        return

    if data.get('rates'):
        bot.send_message(message.chat.id, '$ {:.2f}'.format(value * float(data.get('rates')[currency])))


@bot.message_handler(commands=['history'])
def rate_history(message):
    request = message.text
    res = re.search(r'/history ([A-Z]{3})/([A-Z]{3}) for ([0-9]{1,3}) days$', request)
    if not res:
        bot.send_message(message.chat.id, "Wrong format\nEX: /history USD/CAD for 7 days")
        return
    cur1, cur2, time = res.group(1), res.group(2), res.group(3)

    data = db.get_request(cur1 + cur2 + time, TIME_THRESHOLD)
    if not data:
        start_date = datetime.datetime.now().date() - datetime.timedelta(days=int(time))
        end_date = datetime.datetime.now().date()
        r = requests.get('https://api.exchangeratesapi.io/history?start_at={}&end_at={}&base={}&symbols={}'.format(
            start_date, end_date, cur1, cur2))
        if r.status_code == 400:
            bot.send_message(message.chat.id, "No such currency")
            return
        elif not r.status_code == 200:
            bot.send_message(message.chat.id, "Excange api connection error")
            return
        data = r.text
        db.write(cur1 + cur2 + time, data, datetime.datetime.now())

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        bot.reply_to(message.chat.id, "Response decode error")
        return

    print(data)
    print(sorted([(k, v.get(cur2)) for k, v in data['rates'].items()], key=lambda x: x[0]))
    #
    # if data.get('rates'):
    #     bot.send_message(message.chat.id, '$ {:.2f}'.format(value * float(data.get('rates')[currency])))


bot.polling()

# data = db.get_request('list', TIME_THRESHOLD)
# print(data)
# print('qwe{val:8.2f}'.format(val=13.1123123))
# db.write('test', 'body test 2', datetime.datetime.now() - datetime.timedelta(days=7))

# qwe = {'content_type': 'text', 'message_id': 18,
#        'from_user': {'id': 370615464, 'is_bot': False, 'first_name': 'Роман', 'username': None, 'last_name': 'Хиленко',
#                      'language_code': 'ru'}, 'date': 1580740102,
#        'chat': {'type': 'private', 'last_name': 'Хиленко', 'first_name': 'Роман', 'username': None, 'id': 370615464,
#                 'title': None, 'all_members_are_administrators': None, 'photo': None, 'description': None,
#                 'invite_link': None, 'pinned_message': None, 'sticker_set_name': None, 'can_set_sticker_set': None},
#        'forward_from_chat': None, 'forward_from_message_id': None, 'forward_from': None, 'forward_date': None,
#        'reply_to_message': None, 'edit_date': None, 'media_group_id': None, 'author_signature': None,
#        'text': '/history USD/CAD for 7 days', 'entities': '[<telebot.types.MessageEntity object at 0x7faee27e7dd0>]',
#        'caption_entities': None, 'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None,
#        'video_note': None, 'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None,
#        'animation': None, 'new_chat_member': None, 'new_chat_members': None, 'left_chat_member': None,
#        'new_chat_title': None, 'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None,
#        'supergroup_chat_created': None, 'channel_chat_created': None, 'migrate_to_chat_id': None,
#        'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None, 'successful_payment': None,
#        'connected_website': None, 'json': {'message_id': 18,
#                                            'from': {'id': 370615464, 'is_bot': False, 'first_name': 'Роман',
#                                                     'last_name': 'Хиленко', 'language_code': 'ru'},
#                                            'chat': {'id': 370615464, 'first_name': 'Роман', 'last_name': 'Хиленко',
#                                                     'type': 'private'}, 'date': 1580740102,
#                                            'text': '/exchange $10 to CAD',
#                                            'entities': [{'offset': 0, 'length': 9, 'type': 'bot_command'}]}}
# rate_history(qwe)
# print(db.get_request('request', datetime.datetime.now() + datetime.timedelta(hours=1)))

# bot.reply_to(message, "Howdy, how are you doing?")
# bot.send_message(message.chat.id, "Howdy, how are you doing?")
