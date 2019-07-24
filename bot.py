# -*- coding: utf-8 -*-
import os
import random

import threading
import time
import traceback

import telebot
from pymongo import MongoClient

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)

client = MongoClient(os.environ['database'])
db = client.chatpets
users = db.users
chats = db.chats
lost = db.lost
chat_admins=db.chat_admins

ban = []
totalban = [243153864, 866706209, 500238135]
block=[-1001365421933]


if lost.find_one({'amount': {'$exists': True}}) is None:
    lost.insert_one({'amount': 0})

botname = 'Chatpetsbot'
admin_id = 441399484


@bot.message_handler(commands=['send'])
def sendd(m):
    if is_from_admin(m):
        try:
            text = ''
            i = 2
            a = m.text.split(' ')
            while i < len(a):
                text += a[i] + ' '
                i += 1
            bot.send_message(m.text.split(' ')[1], text)
        except:
            pass


@bot.message_handler(commands=['showlvl'])
def lvlvlvlvl(m):
    if is_from_admin(m):
        try:
            pet = {'lvl': int(m.text.split(' ')[1])}
            x = nextlvl(pet)
            bot.send_message(m.chat.id, str(x))
        except:
            pass

        
@bot.message_handler(commands=['donate'])
def donate(m):
    text='Для совершения добровольного пожертвования можно использовать Сбербанк.'+\
    'Номер карты: `5336 6900 5562 4037`\nЗаранее благодарю!'
    bot.send_message(m.chat.id, text, parse_mode='markdown')
        

@bot.message_handler(commands=['do'])
def do(m):
    if is_from_admin(m):
        try:
            x = m.text.split('/do ')[1]
            try:
                eval(x)
            except:
                bot.send_message(441399484, traceback.format_exc())
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['stop'])
def stopp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': int(m.text.split(' ')[1])}, {'$set': {'spying': None}})
            bot.send_message(m.chat.id, 'success')
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['showchat'])
def showchat(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': int(m.text.split(' ')[1])}, {'$set': {'spying': m.chat.id}})
            bot.send_message(m.chat.id, 'success')
        except:
            bot.send_message(441399484, traceback.format_exc())


@bot.message_handler(commands=['growpet'])
def grow(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is not None:
        bot.send_message(m.chat.id, 'У вас уже есть лошадь!')
        return

    chats.insert_one(createpet(m.chat.id))
    bot.send_message(m.chat.id,
                     'Поздравляю! Вы завели лошадь! О том, как за ней ухаживать, можно прочитать в /help.')


    
@bot.message_handler(commands=['set_admin'])
def set_admin(m):
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status == 'creator':
        if m.reply_to_message!=None:
            chatt=chat_admins.find_one({'id':m.chat.id})
            if chatt==None:
                chat_admins.insert_one(createchatadmins(m))
                chatt=chat_admins.find_one({'id':m.chat.id})
            if int(m.reply_to_message.from_user.id) not in chatt['admins']:
                chat_admins.update_one({'id':m.chat.id},{'$push':{'admins':int(m.reply_to_message.from_user.id)}})
                bot.send_message(m.chat.id, 'Успешно установлен админ лошади: '+m.reply_to_message.from_user.first_name)
            else:
                bot.send_message(m.chat.id, 'Этот юзер уже является администратором лошади!')
        else:
            bot.send_message(m.chat.id, 'Сделайте реплай на сообщение цели!')
    else:
        bot.send_message(m.chat.id, 'Только создатель чата может делать это!')
                    
    
@bot.message_handler(commands=['remove_admin'])
def remove_admin(m):
    user = bot.get_chat_member(m.chat.id, m.from_user.id)
    if user.status == 'creator':
        if m.reply_to_message!=None:
            chatt=chat_admins.find_one({'id':m.chat.id})
            if chatt==None:
                chat_admins.insert_one(createchatadmins(m))
                chatt=chat_admins.find_one({'id':m.chat.id})
            if int(m.reply_to_message.from_user.id) in chatt['admins']:
                chat_admins.update_one({'id':m.chat.id},{'$pull':{'admins':int(m.reply_to_message.from_user.id)}})
                bot.send_message(m.chat.id, 'Успешно удалён админ лошади: '+m.reply_to_message.from_user.first_name+'.')
            else:
                bot.send_message(m.chat.id, 'Этот юзер не является администратором лошади!')
        else:
            bot.send_message(m.chat.id, 'Сделайте реплай на сообщение цели!')
    else:
        bot.send_message(m.chat.id, 'Только создатель чата может делать это!')
    
    
    
def createchatadmins(m):
    return {
        'id':m.chat.id, 
        'admins':[]
    }
    
@bot.message_handler(commands=['getids'])
def idssssss(m):
    if is_from_admin(m):
        text = ''
        for h in lost.find({'id': {'$exists': True}}):
            text += str(h['id']) + ' ' + h['name'] + '\n'
        bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['feed'])
def feeed(m):
    x = chats.find_one({'id': m.chat.id})
    if x is None:
        bot.send_message(m.chat.id, 'А гладить некого:(')
        return

    spisok = ['яблоко', 'сено', 'хлеб', 'шоколадку', 'кукурузу', 'сахар', 'траву', 'рыбу', 'сосиску', 'макароны']
    s2 = ['немного металла', 'мышьяк', 'доску', 'хрен', 'сорняк', 'телефон', 'лошадь', 'автобус', 'компухтер', 'карман']
    if random.randint(1, 100) <= 90:
        s = spisok
    else:
        s = s2
    word = random.choice(s)
    name = m.from_user.first_name
    name = name.replace('*', '').replace('_', '').replace("`", "")
    text = name + ' достаёт из кармана *' + word + '* и кормит ' + x['name'] + '. Лошадь с аппетитом съедает это!'
    bot.send_message(m.chat.id, text, parse_mode='markdown')


@bot.message_handler(commands=['commands'])
def commands(m):
    text = '/feed - покормить лошадь (ни на что не влияет, просто прикол);\n'
    text += '/pogladit - погладить лошадь\n'
    text+='/set_admin (только для создателя чата) - разрешить выбранному юзеру выгонять лошадь из чата\n'
    text+='/remove_admin (только для создателя чата) - запретить юзеру выгонять лошадь (только если ранее ему было это разрешено).\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['getpets'])
def getpet(m):
    if is_from_admin(m):
        db_pets = chats.find().sort('lvl', -1).limit(10)
        text = 'Топ-10 лошадей:\n\n'
        i = 1
        for doc in db_pets:
            text += str(i) + ' место: ' + doc['name'] + ' (' + str(doc['lvl']) + ' лвл) (`' + str(
                doc['id']) + '`)' + '\n'
            i += 1
        try:
            bot.send_message(m.chat.id, text, parse_mode='markdown')
        except:
            bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['rules'])
def rules(m):
    text = '1. Не использовать клиентских ботов для кормления лошади! За это будут наказания.\n2. Не давать рекламу в списке выброшенных лошадей.'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['remove'])
def removee(m):
    if is_from_admin(m):
        try:
            lost.delete_one({'id': int(m.text.split(' ')[1])})
            bot.send_message(m.chat.id, "success")
        except:
            pass


@bot.message_handler(commands=['start'], func=lambda message: is_actual(message))
def startt(m):
    if m.from_user.id == m.chat.id:
        bot.send_message(m.chat.id, 'Здравствуй! /help для информации.')


@bot.message_handler(commands=['info'])
def info(m):
    text = ''
    if not is_from_admin(m):
        return

    for ids in chats.find({}):
        text += str(ids) + '\n\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['top'], func=lambda message: is_actual(message))
def top(m):
    db_pets = chats.find().sort('lvl', -1).limit(10)
    text = 'Топ-10 лошадей:\n\n'
    i = 1
    for doc in db_pets:
        text += str(i) + ' место: ' + doc['name'] + ' (' + str(doc['lvl']) + ' лвл)\n'
        i += 1

    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['help'], func=lambda message: is_actual(message))
def help(m):
    text = ''
    text += 'Чатовые питомцы питаются активностью юзеров. Чем больше вы общаетесь в чате, тем счастливее будет питомец! '
    text += 'Если долго не общаться, питомец начинает голодать и терять жизни. Назвать питомца можно командой /name\n'
    text += 'Для получения опыта необходимо иметь 85% сытости. Для получения бонусного опыта - 95% и 99% (за каждую отметку дается x опыта. То есть если у вас 95% сытости, вы получите (базовый_опыт + х), а если 99%, то (базовый_опыт + 2х).'
    bot.send_message(m.chat.id, text)


@bot.message_handler(func=lambda message: message.migrate_from_chat_id is not None, content_types=None)
def migrate(m):
    old_chat_id = m.migrate_from_chat_id
    new_chat_id = m.chat.id
    if chats.find_one({'id': old_chat_id}) is not None:
        chats.update_one({'id': old_chat_id}, {'$set': {'id': new_chat_id}})


@bot.message_handler(commands=['pogladit'])
def gladit(m):
    try:
        x = chats.find_one({'id': m.chat.id})
        if x is not None:
            bot.send_message(m.chat.id, m.from_user.first_name + ' погладил(а) ' + x['name'] + '!')
        else:
            bot.send_message(m.chat.id, 'А гладить некого!')
    except:
        bot.send_message(admin_id, traceback.format_exc())


@bot.message_handler(commands=['addexp'])
def addexp(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'exp': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['addlvl'])
def addlvl(m):
    if is_from_admin(m):
        try:
            chats.update_one({'id': m.chat.id}, {'$inc': {'lvl': int(m.text.split(' ')[1])}})
        except:
            pass


@bot.message_handler(commands=['petstats'], func=lambda message: is_actual(message))
def petstats(m):
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        bot.send_message(m.chat.id, 'Сначала лошадь нужно завести (или подобрать с улицы)')
        return

    text = ''
    text += '🐴Имя: ' + animal['name'] + '\n'
    text += '🏅Уровень: ' + str(animal['lvl']) + '\n'
    text += '🔥Опыт: ' + str(animal['exp']) + '/' + str(nextlvl(animal)) + '\n'
    text += '♥Здоровье: ' + str(animal['hp']) + '/' + str(animal['maxhp']) + '\n'
    p = int(animal['hunger'] / animal['maxhunger'] * 100)
    text += '🍔Сытость: ' + str(animal['hunger']) + '/' + str(animal['maxhunger']) + ' (' + str(p) + '%)' + '\n'
    text += 'Нужно сытости для постоянного получения опыта: ' + str(int(animal['maxhunger'] * 0.85))
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['losthorses'], func=lambda message: is_actual(message))
def losthorses(m):
    if lost.count_documents({'id': {'$exists': True}}) == 0:
        bot.send_message(m.chat.id, "На улице лошадей нет!")
        return

    text = 'Чтобы забрать лошадь, введите команду /takeh id\n\n'
    for pet in lost.find({'id': {'$exists': True}}):
        text += str(pet['id']) + ': ' + pet['name'] + " (" + str(pet['lvl']) + ' лвл)' + '\n'
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['takeh'], func=lambda message: is_actual(message))
def takeh(m):
    try:
        horse_id = int(m.text.split(' ')[1])
        if lost.find_one({'id': horse_id}) is None:
            bot.send_message(m.chat.id, "Лошадь не существует!")
            return

        if chats.find_one({'id': m.chat.id}) is not None:
            bot.send_message(m.chat.id, "У вас уже есть лошадь!")
            return

        take_horse(horse_id, m.chat.id)
        chats.update_one({'id': horse_id}, {'$set': {'id': m.chat.id}})
        bot.send_message(m.chat.id,
                         "Поздравляем, вы спасли лошадь от голода! Следите за ней, чтобы она росла и не умирала!")
    except:
        pass


def unban(id):
    try:
        ban.remove(id)
    except:
        pass


@bot.message_handler(commands=['throwh'], func=lambda message: is_actual(message))
def throwh(m):
    if m.chat.id not in ban:
        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        ch=chat_admins.find_one({'id':m.chat.id})
        if ch==None:
            if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                    m) and m.from_user.id != m.chat.id:
                bot.send_message(m.chat.id, 'Только админ может делать это!')
                return
        else:
            if m.from_user.id not in ch['admins']:
                bot.send_message(m.chat.id, 'Только админ лошади может делать это! Выставить админов может создатель чата по команде: /set_admin. Убрать админа можно командой /remove_admin.')
                return
    
        if chats.find_one({'id': m.chat.id}) is None:
            bot.send_message(m.chat.id, "У вас даже лошади нет, а вы ее выкидывать собрались :(")
            return
    
        if lose_horse(m.chat.id):
            ban.append(m.chat.id)
            t = threading.Timer(3600, unban, args=[m.chat.id])
            t.start()
            bot.send_message(m.chat.id,
                             "Вы выбросили лошадь на улицу... Если ее никто не подберет, она умрет от голода!")
        else:
            bot.send_message(m.chat.id,
                                 "На улице гуляет слишком много лошадей, поэтому, как только вы ее выкинули, лошадь украли цыгане!")
    else:
        bot.send_message(m.chat.id, 'Можно выгонять только одну лошадь в час!')


@bot.message_handler(commands=['ban'])
def bannn(m):
    if is_from_admin(m):
        try:
            totalban.append(int(m.text.split(' ')[1]))
            bot.send_message(m.chat.id, 'Success')
        except:
            pass


@bot.message_handler(commands=['name'], func=lambda message: is_actual(message))
def name(m):
    try:
        if m.chat.id in totalban and m.from_user.id not in totalban:
            bot.send_message(m.chat.id,
                             'Вам было запрещено менять имя лошади! Разбан через рандомное время (1 минута - 24 часа).')
            return

        user = bot.get_chat_member(m.chat.id, m.from_user.id)
        if user.status != 'creator' and user.status != 'administrator' and not is_from_admin(
                m) and m.from_user.id != m.chat.id:
            bot.send_message(m.chat.id, 'Только админ может делать это!')
            return

        name = m.text.split('/name ')[1]

        if chats.find_one({'id': m.chat.id}) is None:
            return

        if len(name) > 50:
            bot.send_message(m.chat.id, "Максимальная длина имени - 50 символов!")
            return
        if len(name) < 2:
            bot.send_message(m.chat.id, "Минимальная длина имени - 2 символа!")
            return
        chats.update_one({'id': m.chat.id}, {'$set': {'name': name}})
        try:
            bot.send_message(admin_id,
                             str(m.from_user.id) + ' ' + m.from_user.first_name + ' (имя: ' + name + ')')
        except:
            pass
        bot.send_message(m.chat.id, 'Вы успешно сменили имя лошади на ' + name + '!')
    except:
        bot.send_message(admin_id, traceback.format_exc())


@bot.message_handler(commands=['allinfo'])
def allinfo(m):
    if is_from_admin(m):
        text = str(chats.find_one({'id': m.chat.id}))
        bot.send_message(admin_id, text)


@bot.message_handler(commands=['igogo'])
def announce(m):
    if not is_from_admin(m):
        return

    text = m.text.replace('/igogo ', '', 1)
    chats_ids = chats.find({})
    i = 0
    for doc in chats_ids:
        try:
            bot.send_message(doc['id'], text)
            i += 1
        except:
            pass
    bot.send_message(m.chat.id, 'success')#"Сообщение успешно получило " + str(i) + '/' + str(chats.count_documents()) + " чатиков")


@bot.message_handler(func=lambda message: not is_actual(message))
def skip_message(m):
    print('old message skipped')

def is_actual(m):
    return m.date + 120 > int(round(time.time()))


@bot.message_handler(content_types=['text'])
def messages(m):
  if m.chat.id not in block:
    animal = chats.find_one({'id': m.chat.id})
    if animal is None:
        return

    if m.from_user.id not in animal['lastminutefeed']:
        chats.update_one({'id': m.chat.id}, {'$push': {'lastminutefeed': m.from_user.id}})
    if m.chat.title != animal['title']:
        chats.update_one({'id': m.chat.id}, {'$set': {'title': m.chat.title}})
    try:
        if animal['spying'] is not None:
            bot.send_message(animal['spying'], '(Name: ' + m.from_user.first_name + ') (id: ' + str(
                m.from_user.id) + ') (text: ' + m.text + ')')
    except:
        pass


def createpet(id, typee='horse', name='Без имени'):
    return {
        'id': id,
        'type': typee,
        'name': name,
        'lvl': 1,
        'exp': 0,
        'hp': 100,
        'maxhp': 100,
        'lastminutefeed': [],  # Список юзеров, которые проявляли актив в последнюю минуту
        'hunger': 100,
        'maxhunger': 100,
        'title': None,  # Имя чата
        'stats': {},  # Статы игроков: кто сколько кормит лошадь итд
        'spying': None
    }


def medit(message_text, chat_id, message_id, reply_markup=None, parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message_text, reply_markup=reply_markup,
                                 parse_mode=parse_mode)


def nextlvl(pet):
    return pet['lvl'] * (4 + pet['lvl'] * 100)


def check_hunger(pet, horse_lost):
    hunger = pet['hunger']
    maxhunger = pet['maxhunger']
    exp = pet['exp']
    lvl = pet['lvl']
    lastminutefeed = pet['lastminutefeed']

    # если кто-то писал в чат, прибавить кол-во еды равное кол-во покормивших в эту минуту * 2
    if len(lastminutefeed) > 0:
        hunger += len(lastminutefeed) * 2
        lastminutefeed = []
        if hunger > maxhunger:
            hunger = maxhunger

    # если лошадь накормлена на 85% и выше, прибавить опыта
    h = hunger / maxhunger * 100
    if h >= 85:
        exp += int(lvl * (2 + (random.randint(-100, 100) / 100)))
    if h >= 90:
        exp += lvl
    if h >= 99:
        exp += lvl
    if exp >= nextlvl(pet):
        lvl += 1
        maxhunger += 15
        if not horse_lost:
            send_message(pet['id'], 'Уровень вашей лошади повышен! Максимальный запас сытости увеличен на 15!')

    commit = {'hunger': hunger, 'maxhunger': maxhunger, 'exp': exp, 'lvl': lvl, 'lastminutefeed': lastminutefeed}
    if not horse_lost:
        chats.update_one({'id': pet['id']}, {'$set': commit})
    else:
        lost.update_one({'id': pet['id']}, {'$set': commit})


def check_hp(pet, horse_lost):
    hunger = pet['hunger'] - random.randint(3, 9)
    maxhunger = pet['maxhunger']  # const
    hp = pet['hp']
    maxhp = pet['maxhp']  # const

    if hunger <= 0:
        hunger = 0
        if not horse_lost:
            send_message(pet['id'], 'Ваша лошадь СИЛЬНО голодает! Осталось ' + str(
                hunger) + ' сытости! СРОЧНО нужен актив в чат!')
        hp -= random.randint(9, 15)

    elif hunger / maxhunger * 100 <= 30:
        if not horse_lost:
            send_message(pet['id'], 'Ваша лошадь голодает! Осталось всего ' + str(
                hunger) + ' сытости! Срочно нужен актив в чат!')
        hp -= random.randint(9, 15)

    elif hunger / maxhunger * 100 >= 75 and hp < maxhp:
        hp += random.randint(3, 9)
        if hp > maxhp:
            hp = maxhp

    if hp <= 0:
        total = lost.find_one({})['amount']
        total += 1
        lost.update_one({'amount': {'$exists': True}}, {'$inc': {'amount': 1}})
        if not horse_lost:
            chats.delete_one({'id': pet['id']})
            try:
                bot.send_message(pet['id'],
                                 'Вашей лошади плохо в вашем чате, ей не хватает питания. Поэтому я забираю её, чтобы не откинула копыта.\n' +
                                 'Количество лошадей, которых мне пришлось забрать (во всех чатах): ' + str(total))
            except:
                pass
        else:
            lost.delete_one({'id': pet['id']})

    else:
        commit = {'hunger': hunger, 'hp': hp}
        if not horse_lost:
            chats.update_one({'id': pet['id']}, {'$set': commit})
        else:
            lost.update_one({'id': pet['id']}, {'$set': commit})


def check_all_pets_hunger():
    for pet in lost.find({'id': {'$exists': True}}):
        check_hunger(pet, True)
    for pet in chats.find({}):
        check_hunger(pet, False)
    threading.Timer(60, check_all_pets_hunger).start()


def check_all_pets_hp():
    for pet in lost.find({'id': {'$exists': True}}):
        check_hp(pet, True)
    for pet in chats.find({}):
        check_hp(pet, False)
    threading.Timer(1800, check_all_pets_hp).start()


def send_message(chat_id, text):  # использовать только чтобы проверить что лошадь все еще в чате
    try:
        bot.send_message(chat_id, text)
    except:
        lose_horse(chat_id)


def lose_horse(chat_id):  # returns True on success
    pet = chats.find_one({'id': chat_id})
    chats.delete_one({'id': chat_id})

    lost.insert_one(pet)
    horse_id = lost.count_documents({'id': {'$exists': True}})
    while lost.find_one({'id': horse_id}) is not None:
        horse_id += 1
    lost.update_one({'id': chat_id}, {'$set': {'id': horse_id}})
    return True


def take_horse(horse_id, new_chat_id):
    lost.update_one({'id': horse_id}, {'$set': {'id': new_chat_id}})
    pet = lost.find_one({'id': new_chat_id})
    lost.delete_one({'id': new_chat_id})
    chats.insert_one(pet)


def is_from_admin(m):
    return m.from_user.id == admin_id


check_all_pets_hunger()
check_all_pets_hp()

print('7777')
bot.polling(none_stop=True, timeout=600)
