import telebot as tt
from datetime import datetime as dt
from database import *
import os
import pytz
import time as tm
import dotenv as env

# ___________________________________________________UTILS____________________________________________________________ #

help_strings = {
    'take': '_Для того чтобы занять очередь, есть два способа\.\n\n1\) Напишите_ `/take arg`_, где arg \- номер какой\-либо номер очереди\. '
            'Учтите, что вы сразу займете очередь, написав_ `/take arg`\.\n\n_Пример использования: _\n`/take '
            '1`\n\n_2\) Напишите _`/take`_ без аргументов, тогда появится клавиатура с выбором очереди\. После этого '
            'нажмите на очередь, чтобы занять ее\n\nВ случае '
            'фальстарта, бот ответит "Слишком рано" и время получения вашего сообщения\. Если же '
            'фальстарта нет, бот ответит "Время получения запроса: time"\.\n\nНомер и имя занимаемой очереди можно '
            'посмотреть в_ `/queues`',
    'status': '_Для того чтобы посмотреть свой номер в очереди, напишите_ `/status`_, затем просто выберите одну из '
              'предложенных очередей\.\n\nПример использования: _\n`/status`\n\n_В случае если вас нет в'
              'очереди, бот ответит "Вы не заняли очередь :\(", а если есть, тогда он вернет номер в '
              'очереди\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'list': '_Для того чтобы посмотреть очередь, напишите_ `/list`_, затем просто выберите одну из '
            'предложенных очередей\.\n\nПример использования: _\n`/list`\n\n_В случае если очереди нет, бот ответит "Такой '
            'очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет очередь \('
            'если очередь пуста бот вернет "Никто не занял очередь :\("\)\.\n\nНомер и имя занимаемой очереди можно '
            'посмотреть в_ `/queues`',
    'exchange': '_Для того чтобы поменяться местами в очереди, напишите_ `/exchange`_, затем просто выберите одну из '
                'предложенных очередей\. Затем появится новое меню с людьми в очереди\. Выберите того с кем хотите '
                'поменяться\. После выбора ему отправится уведомление о том, что с ним хотят поменяться\. Если второй '
                'человек поменяется с вами местами, вам придет сообщение, что второй человек подтвердил обмен\n\nПример '
                'использования: _\n`/exchange`\n\n_В случае если очереди нет, бот ответит "Такой очереди нет, '
                'посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет очередь \(если очередь '
                'пуста бот вернет "Никто не занял очередь :\("\)\. Если же человека с таким номером не существует, '
                'то бот напишет "Такого номера не существует"\. Если существует, то есть два варианта развитися '
                'событий:\n\n1\) Вы запросили обмен первым, тогда бот напишет, что заявка на обмен принята и начато '
                'ожидание заявки второго человека\.\n2\) Вы запросили обмен вторым, тогда бот напишет, что заявка '
                'принята и очередь изменена\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`_\. Номер '
                'человека в очереди посмотрите с помощью _`/list`_ \(Смотрите _`/help list`_\)_',
    'cancel': '_Для того чтобы отменить свое участие в очереди, напишите_ `/cancel`_, затем просто выберите одну из '
              'предложенных очередей\.\n\nПример использования: _\n`/cancel`\n\n_Номер и имя занимаемой очереди '
              'можно посмотреть в_ `/queues`',
    'edit': '_Для того чтобы изменить свое имя в очереди, напишите_ `/edit`_, затем просто выберите одну из '
            'предложенных очередей\. После напишите имя, на которое хотите изменить текущее имя\n\nПример использования: _\n`/edit '
            '\nЮрий Луцик`\n\n_В случае если нет такой очереди, бот ответит "Такой очереди нет, посмотрите список '
            'доступных очередей в `/queues`", а если есть, тогда он вернет "Готово"\.\n\nНомер и имя занимаемой '
            'очереди можно посмотреть в_ `/queues`',
    'time': '_Для того чтобы посмотреть время занятия очереди, напишите_ `/time`_, затем просто выберите одну из '
            'предложенных очередей\.\n\nПример использования: _\n`/time`\n\n_В случае если нет такой очереди, бот ответит '
            '"Такой очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет '
            'время занятия очереди\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'queues': '_Для того чтобы посмотреть все очереди, напишите_ `/queues`_\n\nПример использования: '
              '_\n`/queues`\n\n_В случае если нет ни одной очереди, бот ответит "Нет ни одной очереди :\(", '
              'а если есть, тогда он вернет список очередей\._',
    'ban': '_Если вы были забанены ботом, эта функция вернет количество секунд до разбана_'
}

help_admin_strings = {
    'admin_create': '_Создает очередь, просто напиши _`/admin_create`_, затем введи имя очереди, и наконец дату и время занятия очереди_',
    'admin_delete': '_Удаляет очередь, напиши _`/admin_delete`_, потом выбери одну из предложенных очередей_',
    'admin_remove': '_Читерская функция, удаляет негодников из очереди\. Напиши _`/admin_remove`_, затем выбери одну из предложенных очередей\. Потом появится еще меню с людьми в очереди, тыкни по тому, кого хочешь удалить_',
    'admin_edit': '_Читерская функция, изменяет имя какому\-нибудь придурку\. Напиши _`/admin_edit`_, затем выбери одну из предложенных очередей\. Потом появится еще меню с людьми в очереди, тыкни по тому, кого хочешь изменить\. После этого напиши ему новое имя_',
    'admin_change': '_Читерская функция, меняет двух челиков\. Напиши _`/admin_change`_, затем выбери одну из предложенных очередей\. После этого напиши два номера челиков из этой очереди, чтобы поменять их_',
    'admin_time': '_Меняет время занятия в очередь, просто напиши _`/admin_time`_, выбери одну из предложенных очередей, и измени ей дату и время занятия очереди_'
}

spams = {}
msgs = 4
maxim = 1
ban = 300

# _______________________________________________CONFIGURATION________________________________________________________ #


env.load_dotenv()
config = {}
if os.getenv("BOT_ENV") == "local":
    config['db_name'] = os.getenv('BOT_LOCAL_DB_NAME')
elif os.getenv("BOT_ENV") == "docker":
    config['db_name'] = os.getenv('BOT_DOCKER_DB_NAME')
config['token'] = os.getenv('BOT_TOKEN')
config['db_admin'] = os.getenv('BOT_DB_ADMIN')
config['db_tables'] = os.getenv('BOT_DB_TABLES')
config['group'] = os.getenv('BOT_GROUP')
config['pass'] = os.getenv('BOT_PASS')

bot = tt.TeleBot(token=config['token'], parse_mode=None, num_threads=6)

con, cursor = database_connect(config['db_name'])
db_init_admin(con, cursor)
tables_database_init(con, cursor)
db_init_users(con, cursor)
close_connection(con, cursor)


def is_spam(user_id: int) -> bool:
    try:
        usr = spams[user_id]
        usr["messages"] += 1
    except Exception as e:
        spams[user_id] = {"next_time": int(tm.time()) + maxim, "messages": 1, "banned": 0}
        usr = spams[user_id]
    if usr["banned"] >= int(tm.time()):
        return True
    else:
        if usr["next_time"] >= int(tm.time()):
            if usr["messages"] >= msgs:
                spams[user_id]["banned"] = tm.time() + ban
                text = """Хотел поспамить? Получай бан на {} минут""".format(ban / 60)
                bot.send_message(user_id, text)
                return True
        else:
            spams[user_id]["messages"] = 1
            spams[user_id]["next_time"] = int(tm.time()) + maxim
    return False


def is_logged(user_id: int) -> bool:
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        users = get_all_users(con_l, cursor_l)
        for user in users:
            if str(user[1]) == str(user_id):
                return True
        close_connection(con_l, cursor_l)
        bot.send_message(user_id, "Выполните вход в систему /login")
    except Exception as e:
        print("FUNC: callback_login_handler ERR:", e)
    return False


# __________________________________________TELEGRAM BOT HANDLERS_____________________________________________________ #

# __________________________________________USER COMMANDS HANDLERS____________________________________________________ #


@bot.message_handler(commands=['start'])
def handle_start(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id, parse_mode='MarkdownV2',
                     text='`/take` \- _Занять очередь_\n`/status` \- _Посмотреть какой ты по счету в очереди_\n`/list` \- _Посмотреть всю очередь_\n`/change` \- _Поменяться местами с кем\-либо в очереди_\n`/cancel` \- _Перехотел сдавать_\n`/edit` \- _Изменить имя в очереди_\n`/queues` \- _Посмотреть список очередей_\n`/time` \- _Посмотреть во сколько нужно занимать в очереди_\n`/ban` \- _Посмотреть, сколько секунд осталось до разбана_')
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, parse_mode='MarkdownV2',
                         text='_Для админов_\n`/admin_create` \- _Создать очередь_\n`/admin_delete` \- _Удалить очередь_\n`/admin_time` \- _Изменить время занятия очереди_\n`/admin_edit` \- _Принудительно изменяет имя человека, занявшего очередь_\n`/admin_remove` \- _Принудительно удаляет человека из очереди_\n`/admin_change` \- _Принудительно меняет двух человек местами_')
    bot.send_message(message.chat.id, text="Напиши `/help имя\_команды`, чтобы узнать о ней подробнее",
                     parse_mode='MarkdownV2')
    bot.send_message(message.chat.id,
                     text="Предупреждаю, в боте стоит антиспам система, если вы начнете спамить вам выдадут бан на 5 минут, если это вас не остановит, вас еще и тг забанит на неопределенное время.")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['login'])
def login(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if is_logged(message.chat.id):
        bot.send_message(message.chat.id, text="Вы уже залогинились")
        return
    bot.send_message(message.chat.id, 'Введите номер группы')
    bot.register_next_step_handler(message, callback_login_handler)


def callback_login_handler(message):
    try:
        if message.text == config['group']:
            con_l, cursor_l = database_connect(config['db_name'])
            insert_user(con_l, cursor_l, {"tg_id": message.chat.id,
                                          "username": f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                          "points": 0})
            bot.send_message(message.chat.id, 'Вы вошли в систему!')
            close_connection(con_l, cursor_l)
        else:
            bot.send_message(message.chat.id, text="Понятия не имею, кто ты, герой")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_login_handler ERR:", e)


@bot.message_handler(commands=['help'])
def handle_help(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    markup = tt.types.InlineKeyboardMarkup()
    for command in help_strings:
        markup.add(tt.types.InlineKeyboardButton(f"{command}", callback_data=f"helpbutton {command}"))
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, str(message.chat.id)):
        for command in help_admin_strings:
            markup.add(tt.types.InlineKeyboardButton(f"{command}", callback_data=f"helpbutton {command}"))
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('helpbutton'))
def callback_query_help(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    command = call.data[11:]
    if help_strings.get(command):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text=help_strings[command], parse_mode="MarkdownV2")
    elif help_admin_strings.get(command):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text=help_admin_strings[command], parse_mode="MarkdownV2")
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text='Такой команды нет')
        bot.send_message(call.message.chat.id, text='Ознакомьтесь с перечнем команд, написав `/start` или `/help`',
                         parse_mode='MarkdownV2')


@bot.message_handler(commands=['take'])
def handle_take(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    try:
        no = tt.util.extract_arguments(message.text)
        no = int(no)
        try:
            con_l, cursor_l = database_connect(config['db_name'])
            datetime = get_table_time(con_l, cursor_l, no).split(' ')
            day, month, year = map(int, datetime[0].split('-'))
            hour, minute = map(int, datetime[1].split(':'))
            time = dt.now(pytz.timezone('Europe/Minsk'))
            time = time.replace(tzinfo=None)
            if time < dt.strptime(f'{day}-{month}-{year} {hour}:{minute}', '%d-%m-%Y %H:%M'):
                bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
                return
            table_name = get_table_name(con_l, cursor_l, int(no))
            lst = get_all(con_l, cursor_l, table_name)
            if lst is not None:
                for human in lst:
                    if human[1] == str(message.chat.id):
                        close_connection(con_l, cursor_l)
                        bot.send_message(message.chat.id, text=f'Вы уже заняли очередь')
                        return
            time_s = time.strftime("%H:%M:%S:%f")
            insert_value(con_l, cursor_l, {'tg_id': message.chat.id, 'time': time,
                                           'username': f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                           'change': -1}, table_name)
            bot.send_message(message.chat.id,
                             text=f'Время получения запроса: {time_s}')
            bot.send_message(message.chat.id, text=f'Вы заняли очередь в {get_table_name(con_l, cursor_l, no)}')
            close_connection(con_l, cursor_l)
        except Exception as e:
            bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
            print("FUNC: callback_take_handler ERR:", e)
    except Exception as e:
        con_l, cursor_l = database_connect(config['db_name'])
        markup = tt.types.InlineKeyboardMarkup()
        tables = get_all_tables(con_l, cursor_l)
        idx = 1
        if not tables:
            bot.send_message(message.chat.id,
                             text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
            return
        for table in tables:
            markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"takebutton {idx}"))
            idx += 1
        bot.send_message(message.chat.id, "Занять очередь", reply_markup=markup)
        close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('takebutton'))
def callback_query_take(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        no = int(call.data[11:])
        datetime = get_table_time(con_l, cursor_l, no).split(' ')
        day, month, year = map(int, datetime[0].split('-'))
        hour, minute = map(int, datetime[1].split(':'))
        time = dt.now(pytz.timezone('Europe/Minsk'))
        time = time.replace(tzinfo=None)
        if time < dt.strptime(f'{day}-{month}-{year} {hour}:{minute}', '%d-%m-%Y %H:%M'):
            bot.send_message(call.message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
        table_name = get_table_name(con_l, cursor_l, int(no))
        lst = get_all(con_l, cursor_l, table_name)
        if lst is not None:
            for human in lst:
                if human[1] == str(call.message.chat.id):
                    close_connection(con_l, cursor_l)
                    bot.send_message(call.message.chat.id, text=f'Вы уже заняли очередь')
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    return
        time_s = time.strftime("%H:%M:%S:%f")
        insert_value(con_l, cursor_l, {'tg_id': call.message.chat.id, 'time': time,
                                       'username': f"{call.message.chat.first_name if call.message.chat.first_name is not None else ''} {call.message.chat.last_name if call.message.chat.last_name is not None else ''}",
                                       'change': -1}, table_name)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id,
                         text=f'Вы заняли очередь в {get_table_name(con_l, cursor_l, no)}\nВремя: {time_s}')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_take_handler ERR:", e)


@bot.message_handler(commands=['status'])
def handle_status(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"statusbutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('statusbutton'))
def callback_query_status(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[13:])
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        if not get_status_by_id(con_l, cursor_l, str(call.message.chat.id), get_table_name(con_l, cursor_l, no)):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             f"Вы {get_status_by_id(con_l, cursor_l, str(call.message.chat.id), get_table_name(con_l, cursor_l, no))[0][0]} в очереди {get_table_name(con_l, cursor_l, no)}")
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_status_handler ERR:", e)


@bot.message_handler(commands=['list'])
def handle_list(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"listbutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('listbutton'))
def callback_query_list(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[11:])
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        lst = get_all_in_order(con_l, cursor_l, get_table_name(con_l, cursor_l, no))
        if not lst:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text="Никто не занял очередь :(")
            close_connection(con_l, cursor_l)
            return
        else:
            s = f"Очередь {get_table_name(con_l, cursor_l, no)}:\n"
            for human in lst:
                s += f"№{str(human[0])} {str(human[2])} Время: {str(human[3])}\n"
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text=s)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_list_handler ERR:", e)


@bot.message_handler(commands=['exchange'])
def handle_change(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"changebutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('changebutton'))
def callback_query_change(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[13:])
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        lst = get_all(con_l, cursor_l, get_table_name(con_l, cursor_l, no))
        exist = False
        for human in lst:
            if human[1] == str(call.message.chat.id):
                exist = True
        if not exist:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text=f'Ты не занял очередь :(')
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = tt.types.InlineKeyboardMarkup()
        idx = 1
        for human in lst:
            markup.add(tt.types.InlineKeyboardButton(f"№{human[0]} {human[2]}",
                                                     callback_data=f"change2button {human[0]} {get_table_name(con_l, cursor_l, no)}"))
            idx += 1
        bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_change_handler ERR:", e)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('change2button'))
def callback_change_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    no: int
    try:
        data = call.data.split(' ')
        no = int(data[1])
        table_name = data[2]
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, table_name)
        if not lst:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text="Никто не занял очередь :(")
            return
        if len(lst) < no:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text="Такого номера не существует")
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Запрос на изменение очереди принят')
        update_change(con_l, cursor_l, get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0], no,
                      table_name)
        if lst[no - 1][4] == get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0][0] != -1:
            bot.send_message(get_status_by_no(con_l, cursor_l, no, table_name)[0][1],
                             text=f"{get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0][2]} поменялся с тобой (№{get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0][0]})")
            change_queue(con_l, cursor_l, get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0],
                         get_status_by_no(con_l, cursor_l, no, table_name)[0], table_name)
            bot.send_message(call.message.chat.id, 'Очередь изменена')
        else:
            bot.send_message(get_status_by_no(con_l, cursor_l, no, table_name)[0][1],
                             text=f"{get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0][2]} хочет с тобой поменяться (№{get_status_by_id(con_l, cursor_l, str(call.message.chat.id), table_name)[0][0]})")
            bot.send_message(call.message.chat.id,
                             'Второй человек тоже должен поменяться с тобой местом чтобы очередь изменилась')
        close_connection(con_l, cursor_l)

    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        print("FUNC: callback_change2_handler ERR:", e)
        bot.send_message(call.message.chat.id, 'Такого номера не существует')


@bot.message_handler(commands=['cancel'])
def handle_cancel(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"cancelbutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('cancelbutton'))
def callback_query_cancel(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[13:])
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        if not get_status_by_id(con_l, cursor_l, str(call.message.chat.id), get_table_name(con_l, cursor_l, no)):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
            return
        cancel_take(con_l, cursor_l, str(call.message.chat.id), get_table_name(con_l, cursor_l, no))
        close_connection(con_l, cursor_l)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text='Ты освободил свое место в очереди')
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_cancel_handler ERR:", e)


@bot.message_handler(commands=['edit'])
def handle_edit(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"editbutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('editbutton'))
def callback_query_edit(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[11:])
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        if not get_status_by_id(con_l, cursor_l, str(call.message.chat.id), get_table_name(con_l, cursor_l, no)):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text='Напиши имя и фамилию')
        bot.register_next_step_handler(call.message, callback_edit_handler,
                                       get_table_name(con_l, cursor_l, no))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_edit_handler ERR:", e)


def callback_edit_handler(message: tt.types.Message, table_name: str):
    if is_spam(message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        update_name(con_l, cursor_l, str(message.chat.id), message.text, table_name)
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text='Готово')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


@bot.message_handler(commands=['queues'])
def handle_queues(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    tables = get_all_tables(con_l, cursor_l)
    if tables:
        s = 'Очереди:\n'
        idx = 1
        for table in tables:
            s += f"№{str(idx)} {table[1]} {table[3]}\n"
            idx += 1
        bot.send_message(message.chat.id, text=s)
    else:
        bot.send_message(message.chat.id, text="Нет ни одной очереди :(")
        bot.send_message(message.chat.id, text="Если скоро занимать очередь, а ее нет напишите админам")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['time'])
def handle_time(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    idx = 1
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"timebutton {idx}"))
        idx += 1
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('timebutton'))
def callback_query_time(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        no = int(call.data[11:])
        con_l, cursor_l = database_connect(config['db_name'])
        get_table_time(con_l, cursor_l, no)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text=get_table_time(con_l, cursor_l, no))
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_time_handler ERR:", e)


@bot.message_handler(commands=['ban'])
def handle_ban(message: tt.types.Message):
    if is_spam(message.chat.id):
        bot.send_message(message.chat.id,
                         text=f"{int(spams[message.chat.id]['banned'] - int(tm.time()))} секунд осталось до разбана")
        return
    elif not is_logged(message.chat.id):
        return
    else:
        bot.send_message(message.chat.id, text="Вы не забанены")


# __________________________________________ADMIN COMMANDS HANDLERS___________________________________________________ #


@bot.message_handler(commands=['supersecretadmin'])
def handle_admin(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="Ты уже админ")
        return
    bot.send_message(message.chat.id, text="Введи пароль")
    bot.register_next_step_handler(message, callback_admin_handler)
    close_connection(con_l, cursor_l)


def callback_admin_handler(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if message.text != config['pass']:
        bot.send_message(message.chat.id, text="Ты не знаешь пароля ухади!!1!")
        return
    con_l, cursor_l = database_connect(config['db_name'])
    make_admin(con_l, cursor_l, {"tg_id": message.chat.id,
                                 "username": f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}"})
    bot.send_message(message.chat.id, text="Ты админ")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['admin_create'])
def handle_create(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Создание очереди")
    bot.send_message(message.chat.id, text="Введи имя очереди, которую хочешь создать")
    close_connection(con_l, cursor_l)
    bot.register_next_step_handler(message, callback_create_handler)


def callback_create_handler(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    try:
        bot.send_message(message.chat.id,
                         text="Введи время в которое нужно занять очередь, которую хочешь создать (DD-MM HH:MM)")
        bot.register_next_step_handler(message, callback_create2_handler, message.text)
    except Exception as e:
        print("FUNC: callback_create_handler ERR:", e)


def callback_create2_handler(message: tt.types.Message, table_name: str):
    if is_spam(message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        datetime = message.text.split(' ')
        day, month = map(int, datetime[0].split('-'))
        hour, minute = map(int, datetime[1].split(':'))
        tables = get_all_tables(con_l, cursor_l)
        if message.text == 'admins' or message.text == 'tables' or message.text == 'users':
            bot.send_message(message.chat.id, text='Самый умный что-ли?')
            return
        for table in tables:
            if table[1] == message.text:
                bot.send_message(message.chat.id, text='Очередь с таким именем уже существует')
                return
        database_init(con_l, cursor_l, table_name)
        insert_table(con_l, cursor_l, {'name': table_name, 'date': dt.now(pytz.timezone('Europe/Minsk')),
                                       'time': dt.strptime(
                                           f"{day}-{month}-{dt.now(pytz.timezone('Europe/Minsk')).year} {hour}:{minute}",
                                           '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M')})
        bot.send_message(message.chat.id, text=f"Очередь создана")
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_create2_handler ERR:", e)


@bot.message_handler(commands=['admin_delete'])
def handle_delete(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Создай хотя бы одну")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"admindeletebutton {table[1]}"))
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admindeletebutton'))
def callback_query_admin_delete(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    table_name = call.data[18:]
    con_l, cursor_l = database_connect(config['db_name'])
    tables = get_all_tables(con_l, cursor_l)
    exist = False
    if table_name == 'admins' or table_name == 'tables' or table_name == 'users':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text='Самый умный что-ли?')
        return
    for table in tables:
        if table[1] == table_name:
            exist = True
    if not exist:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text='Очередь с таким именем не существует')
        return
    delete_table(con_l, cursor_l, table_name)
    delete_table_from_table(con_l, cursor_l, table_name)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, text=f"Очередь с именем {table_name} удалена")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['admin_time'])
def handle_settime(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    con_l, cursor_l = database_connect(config['db_name'])
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Создай хотя бы одну")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"admintimebutton {table[1]}"))
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admintimebutton'))
def callback_query_admin_time(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        table_name = call.data[16:]
        con_l, cursor_l = database_connect(config['db_name'])
        tables = get_all_tables(con_l, cursor_l)
        exist = False
        no = 0
        if table_name == 'admins' or table_name == 'tables' or table_name == 'users':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Самый умный что-ли?')
            return
        for table in tables:
            if table[1] == table_name:
                exist = True
                break
            no += 1
        if not exist:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Очередь с таким именем не существует')
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text=f"Введи новое время как в примере (DD-MM HH:MM)")
        bot.register_next_step_handler(call.message, callback_settime2_handler, get_table_name(con_l, cursor_l, no + 1))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime_handler ERR:", e)


def callback_settime2_handler(message: tt.types.Message, table_name: str):
    if is_spam(message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        datetime = message.text.split(' ')
        day, month = map(int, datetime[0].split('-'))
        hour, minute = map(int, datetime[1].split(':'))
        if is_exist_table(con_l, cursor_l, table_name):
            set_table_time(con_l, cursor_l, table_name,
                           dt.strptime(f"{day}-{month}-{dt.now(pytz.timezone('Europe/Minsk')).year} {hour}:{minute}",
                                       '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M'))
            bot.send_message(message.chat.id, "Время занятия очереди изменено")
        else:
            print("Нет такой очереди")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime2_handler ERR:", e)


@bot.message_handler(commands=['admin_edit'])
def handle_admin_edit(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Создай хотя бы одну")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"admineditbutton {table[1]}"))
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admineditbutton'))
def callback_query_admin_edit(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        table_name = call.data[16:]
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, table_name):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        markup = tt.types.InlineKeyboardMarkup()
        lst = get_all(con_l, cursor_l, table_name)
        if lst:
            for human in lst:
                markup.add(tt.types.InlineKeyboardButton(f"{human[2]}",
                                                         callback_data=f"adminedit2button {human[0]} {table_name}"))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit_handler ERR:", e)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminedit2button'))
def callback_admin_edit2_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        data = call.data.split(' ')
        db_id = int(data[1])
        table_name = data[2]
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, table_name)
        if lst:
            if len(lst) >= db_id:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, text='Введите имя и фамилию человека')
                bot.register_next_step_handler(call.message, callback_admin_edit3_handler, table_name, db_id)
            else:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, text='Неправильный номер')
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit2_handler ERR:", e)


def callback_admin_edit3_handler(message: tt.types.Message, table_name: str, no: int):
    if is_spam(message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        update_name(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no, table_name)[0][1],
                    message.text, table_name)
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text='Готово')
    except Exception as e:
        print("FUNC: callback_admin_edit3_handler ERR:", e)


@bot.message_handler(commands=['admin_change'])
def handle_admin_change(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Создай хотя бы одну")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"adminchangebutton {table[1]}"))
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminchangebutton'))
def callback_admin_change_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        table_name = call.data[18:]
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, table_name):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, text=f'Введи два номера людей через пробел, которых хочешь поменять')
        bot.register_next_step_handler(call.message, callback_admin_change2_handler, table_name)
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_change_handler ERR:", e)


def callback_admin_change2_handler(message: tt.types.Message, table_name: str):
    if is_spam(message.chat.id):
        return
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, table_name)
        no1, no2 = map(int, message.text.split(' '))
        if lst:
            if len(lst) >= no1 and len(lst) >= no2:
                change_queue(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no1, table_name)[0],
                             get_status_by_no(con_l, cursor_l, no2, table_name)[0], table_name)
                bot.send_message(message.chat.id, 'Очередь изменена')
            else:
                bot.send_message(message.chat.id, text='Неправильный номер')
        else:
            bot.send_message(message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_change2_handler ERR:", e)


@bot.message_handler(commands=['admin_remove'])
def handle_admin_remove(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    markup = tt.types.InlineKeyboardMarkup()
    tables = get_all_tables(con_l, cursor_l)
    if not tables:
        bot.send_message(message.chat.id,
                         text="Нет ни одной очереди. Создай хотя бы одну")
        return
    for table in tables:
        markup.add(tt.types.InlineKeyboardButton(f"{table[1]}", callback_data=f"adminremovebutton {table[1]}"))
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminremovebutton'))
def callback_admin_remove_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        table_name = call.data[18:]
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, table_name):
            close_connection(con_l, cursor_l)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = tt.types.InlineKeyboardMarkup()
        lst = get_all(con_l, cursor_l, table_name)
        for human in lst:
            markup.add(tt.types.InlineKeyboardButton(f"№{human[0]} {human[2]}",
                                                     callback_data=f"adminremove2button {human[0]} {table_name}"))
        bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete_handler ERR:", e)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminremove2button'))
def callback_admin_remove2_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        data = call.data.split(' ')
        no = int(data[1])
        table_name = data[2]
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, table_name)
        if lst:
            if len(lst) >= no:
                cancel_take(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no, table_name)[0][1], table_name)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Удалено')
            else:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, text='Неправильный номер')
        else:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete2_handler ERR:", e)


@bot.message_handler(commands=['admin_list'])
def handle_admin_list(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    admins = get_all_admins(con_l, cursor_l)
    if not admins:
        bot.send_message(message.chat.id,
                         text="Нет ни одного админа")
        return
    s = "Администраторы:\n"
    for admin in admins:
        s += f"{admin[2]}\n"
    bot.send_message(message.chat.id, text=s)
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['admin_kick'])
def handle_admin_kick(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    markup = tt.types.InlineKeyboardMarkup()
    users = get_all_users(con_l, cursor_l)
    if not users:
        bot.send_message(message.chat.id,
                         text="Нет ни одного пользователя")
        return
    for human in users:
        markup.add(tt.types.InlineKeyboardButton(f"{human[2]}", callback_data=f"adminkickbutton {human[1]}"))
    bot.send_message(message.chat.id, "Выбери пользователя", reply_markup=markup)
    close_connection(con_l, cursor_l)


@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminkickbutton'))
def callback_admin_kick_handler(call: tt.types.CallbackQuery):
    if is_spam(call.message.chat.id):
        return
    try:
        data = call.data.split(' ')
        tg_id = data[1]
        con_l, cursor_l = database_connect(config['db_name'])
        remove_admin(con_l, cursor_l, tg_id)
        remove_user(con_l, cursor_l, tg_id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Пользователь удален')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete2_handler ERR:", e)


@bot.message_handler(commands=['admin_users'])
def handle_admin_users(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, str(message.chat.id)):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    users = get_all_users(con_l, cursor_l)
    if not users:
        bot.send_message(message.chat.id,
                         text="Нет ни одного пользователя")
        return
    s = "Пользователи:\n"
    for human in users:
        s += f"{human[2]}, приоритет: {human[3]}\n"
    bot.send_message(message.chat.id, text=s)
    close_connection(con_l, cursor_l)


# @bot.message_handler(commands=['admin_set'])
# def handle_admin_set(message: tt.types.Message):
#     if is_spam(message.chat.id):
#         return
#     if not is_logged(message.chat.id):
#         return
#     con_l, cursor_l = database_connect(config['db_name'])
#     if not is_admin(con_l, cursor_l, str(message.chat.id)):
#         bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
#         return
#     users = get_all_users(con_l, cursor_l)
#     if not users:
#         bot.send_message(message.chat.id,
#                          text="Нет ни одного пользователя")
#         return
#     s = "Пользователи:\n"
#     for human in users:
#         s += f"{human[2]}, приоритет: {human[3]}\n"
#     bot.send_message(message.chat.id, text=s)
#     close_connection(con_l, cursor_l)


@bot.message_handler()
def handler_else(message: tt.types.Message):
    if is_spam(message.chat.id):
        return
    if not is_logged(message.chat.id):
        return


def start():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    start()
