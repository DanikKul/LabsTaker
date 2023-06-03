import telebot as tt
from datetime import datetime as dt
from database import *
import json
import pytz

# ___________________________________________________UTILS____________________________________________________________ #

help_strings = {
    'take': '_Для того чтобы занять очередь, напишите_ `/take arg`_, где arg \- номер какой\-либо номер очереди\. Учтите, что вы сразу займете очередь, написав_ `/take arg`\.\n\n_Пример использования: _\n`/take 1`\n\n_В случае фальстарта, бот ответит "Слишком рано" и время получения вашего сообщения\. Если же фальстарта нет, бот ответит "Время получения запроса: time"\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'status': '_Для того чтобы посмотреть свой номер в очереди, напишите_ `/status arg`_, где arg \- номер какой\-либо номер очереди\.\n\nПример использования: _\n`/status 1`\n\n_В случае если вас нет в очереди, бот ответит "Вы не заняли очередь :\(", а если есть, тогда он вернет номер в очереди\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'list': '_Для того чтобы посмотреть очередь, напишите_ `/list arg`_, где arg \- номер какой\-либо номер очереди\.\n\nПример использования: _\n`/list 1`\n\n_В случае если очереди нет, бот ответит "Такой очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет очередь \(если очередь пуста бот вернет "Никто не занял очередь :\("\)\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'change': '_Для того чтобы поменяться местами в очереди, напишите_ `/change arg`_, где arg \- номер какой\-либо номер очереди\. А затем напишите номер человека в очереди с которым вы хотите поменяться\n\nПример использования: _\n`/change 1\n1`\n\n_В случае если очереди нет, бот ответит "Такой очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет очередь \(если очередь пуста бот вернет "Никто не занял очередь :\("\)\. Если же человека с таким номером не существует, то бот напишет "Такого номера не существует"\. Если существует, то есть два варианта развитися событий:\n\n1\) Вы запросили обмен первым, тогда бот напишет, что заявка на обмен принята и начато ожидание заявки второго человека\.\n2\) Вы запросили обмен вторым, тогда бот напишет, что заявка принята и очередь изменена\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`_\. Номер человека в очереди посмотрите с помощью _`/list`_ \(Смотрите _`/help list`_\)_',
    'cancel': '_Для того чтобы отменить свое участие в очереди, напишите_ `/cancel arg`_, где arg \- номер какой\-либо номер очереди\.\n\nПример использования: _\n`/cancel 1`\n\n_Номер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'edit': '_Для того чтобы изменить свое имя в очереди, напишите_ `/edit arg`_, где arg \- номер какой\-либо номер очереди\. После напишите имя, на которое хотите изменить текущее имя\n\nПример использования: _\n`/edit 1\nЮрий Луцик`\n\n_В случае если нет такой очереди, бот ответит "Такой очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет "Готово"\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'time': '_Для того чтобы посмотреть время занятия очереди, напишите_ `/time arg`_, где arg \- номер какой\-либо номер очереди\.\n\nПример использования: _\n`/time 1`\n\n_В случае если нет такой очереди, бот ответит "Такой очереди нет, посмотрите список доступных очередей в `/queues`", а если есть, тогда он вернет время занятия очереди\.\n\nНомер и имя занимаемой очереди можно посмотреть в_ `/queues`',
    'queues': '_Для того чтобы посмотреть все очереди, напишите_ `/queues`_\n\nПример использования: _\n`/queues`\n\n_В случае если нет ни одной очереди, бот ответит "Нет ни одной очереди :\(", а если есть, тогда он вернет список очередей\._'
}

# _______________________________________________CONFIGURATION________________________________________________________ #

# Read config file
with open('config.json') as fp:
    config = json.load(fp)

# Create telebot object
bot = tt.TeleBot(token=config['token'], parse_mode=None)

# Initialize databases
con, cursor = database_connect(config['db_name'])
admin_db_init(con, cursor)
tables_database_init(con, cursor)
close_connection(con, cursor)


# __________________________________________TELEGRAM BOT HANDLERS_____________________________________________________ #

# __________________________________________USER COMMANDS HANDLERS____________________________________________________ #


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id, parse_mode='MarkdownV2',
                     text='`/take arg` \- _Занять очередь c номером arg_\n`/status arg` \- _Посмотреть какой ты по счету в очереди arg_\n`/list arg` \- _Посмотреть всю очередь arg_\n`/change arg` \- _Поменяться местами с кем\-либо в очереди arg_\n`/cancel arg` \- _Перехотел сдавать в очереди arg_\n`/edit arg` \- _Изменить имя в очереди arg_\n`/queues` \- _Посмотреть список очередей_\n`/time arg` \- _Посмотреть во сколько нужно занимать в очереди arg_')
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, parse_mode='MarkdownV2',
                         text='_Для админов_\n`/admin_create` \- _Создать очередь_\n`/admin_delete` \- _Удалить очередь_\n`/admin_time` \- _Изменить время занятия очереди_\n`/admin_edit` \- _Принудительно изменяет имя человека, занявшего очередь_\n`/admin_remove` \- _Принудительно удаляет человека из очереди_\n`/admin_change` \- _Принудительно меняет двух человек местами_')
    bot.send_message(message.chat.id, text="Напиши `/help имя\_команды`, чтобы узнать о ней подробнее", parse_mode='MarkdownV2')


@bot.message_handler(commands=['help'])
def handle_help(message):
    command: str = tt.util.extract_arguments(message.text)
    if not command:
        handle_start(message)
        return
    command = command.replace('/', '')
    if help_strings.get(command):
        bot.send_message(message.chat.id, text=help_strings[command], parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, text='Такой команды нет')
        bot.send_message(message.chat.id, text='Ознакомьтесь с перечнем команд, написав `/start` или `/help`',
                         parse_mode='MarkdownV2')


@bot.message_handler(commands=['take'])
def handle_take(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        hour, minute = map(int, get_table_time(con_l, cursor_l, no).split(':'))
        time = dt.now(pytz.timezone('Europe/Minsk'))
        if time.hour * 60 + time.minute < hour * 60 + minute:
            bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
            return
        db_name = get_table_name(con_l, cursor_l, int(no))
        lst = get_all(con_l, cursor_l, db_name)
        if lst is not None:
            for human in lst:
                if human[1] == str(message.chat.id):
                    close_connection(con_l, cursor_l)
                    bot.send_message(message.chat.id, text=f'Вы уже заняли очередь')
                    return
        time_s = time.strftime("%H:%M:%S:%f")
        insert_value(con_l, cursor_l, {'tg_id': message.chat.id, 'time': time,
                                       'username': f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                       'change': -1}, db_name)
        bot.send_message(message.chat.id,
                         text=f'Время получения запроса: {time_s}')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_take_handler ERR:", e)


@bot.message_handler(commands=['status'])
def handle_status(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        if not get_status_by_id(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, no)):
            bot.send_message(message.chat.id, f"Вы не заняли очередь :(")
        else:
            bot.send_message(message.chat.id,
                             f"{get_status_by_id(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, no))[0][0]}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_status_handler ERR:", e)


@bot.message_handler(commands=['list'])
def handle_list(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        lst = get_all_in_order(con_l, cursor_l, get_table_name(con_l, cursor_l, no))
        if not lst:
            bot.send_message(message.chat.id, text="Никто не занял очередь :(")
        else:
            s = ""
            for human in lst:
                s += f"№{str(human[0])} {str(human[2])} Время: {str(human[3])}\n"
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=s)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_list_handler ERR:", e)


@bot.message_handler(commands=['change'])
def handle_change(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Введите номер человека с которым хотите поменяться')
        bot.register_next_step_handler(message, callback_change_handler,
                                       get_table_name(con_l, cursor_l, no))
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_change_handler ERR:", e)


def callback_change_handler(message, name):
    no: int
    try:
        no = int(message.text)
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, name)
        if not lst:
            bot.send_message(message.chat.id, text="Никто не занял очередь :(")
            return
        if len(lst) < no:
            bot.send_message(message.chat.id, text="Такого номера не существует")
            return
        bot.send_message(message.chat.id, 'Запрос на изменение очереди принят')
        update_change(con_l, cursor_l, get_status_by_id(con_l, cursor_l, message.chat.id, name)[0], no, name)
        if lst[no - 1][4] == get_status_by_id(con_l, cursor_l, message.chat.id, name)[0][0] != -1:
            change_queue(con_l, cursor_l, get_status_by_id(con_l, cursor_l, message.chat.id, name)[0],
                         get_status_by_no(con_l, cursor_l, no, name)[0], name)
            bot.send_message(message.chat.id, 'Очередь изменена')
        else:
            bot.send_message(message.chat.id,
                             'Второй человек тоже должен поменяться с тобой местом чтобы очередь изменилась')
        close_connection(con_l, cursor_l)

    except Exception as e:
        print("FUNC: callback_change2_handler ERR:", e)
        bot.send_message(message.chat.id, 'Такого номера не существует')


@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        cancel_take(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, no))
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text='Ты освободил свое место в очереди')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_cancel_handler ERR:", e)


@bot.message_handler(commands=['edit'])
def handle_edit(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, no)):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text='Напиши имя и фамилию')
        bot.register_next_step_handler(message, callback_edit_handler,
                                       get_table_name(con_l, cursor_l, no))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_edit_handler ERR:", e)


def callback_edit_handler(message, name):
    con_l, cursor_l = database_connect(config['db_name'])
    update_name(con_l, cursor_l, message.chat.id, message.text, name)
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id, text='Готово')


@bot.message_handler(commands=['queues'])
def handle_queues(message):
    con_l, cursor_l = database_connect(config['db_name'])
    tables = get_all_tables(con_l, cursor_l)
    if tables:
        s = 'Очереди:\n'
        idx = 1
        for table in tables:
            s += f"№{str(idx)} {table[1]}\n"
            idx += 1
        bot.send_message(message.chat.id, text=s)
    else:
        bot.send_message(message.chat.id, text="Нет ни одной очереди :(")
        bot.send_message(message.chat.id, text="Если скоро занимать очередь, а ее нет напишите админам")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['time'])
def handle_time(message):
    try:
        no = tt.util.extract_arguments(message.text)
        if not no:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        no = int(no)
        if no <= 0:
            bot.send_message(message.chat.id, text="Напишите в аргументах команды номер очереди из /queues")
            return
        con_l, cursor_l = database_connect(config['db_name'])
        get_table_time(con_l, cursor_l, no)
        bot.send_message(message.chat.id, text=get_table_time(con_l, cursor_l, no))
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_time_handler ERR:", e)


# __________________________________________ADMIN COMMANDS HANDLERS___________________________________________________ #


@bot.message_handler(commands=['supersecretadmin'])
def handle_admin(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="Ты уже админ")
        return
    bot.send_message(message.chat.id, text="Введи пароль")
    bot.register_next_step_handler(message, callback_admin_handler)
    close_connection(con_l, cursor_l)


def callback_admin_handler(message):
    if message.text != config['pass']:
        bot.send_message(message.chat.id, text="Ты не знаешь пароля ухади!!1!")
        return
    con_l, cursor_l = database_connect(config['db_name'])
    make_admin(con_l, cursor_l, {"tg_id": message.chat.id,
                                 "username": f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}"})
    bot.send_message(message.chat.id, text="Ты админ")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['admin_create'])
def handle_create(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Создание очереди")
    bot.send_message(message.chat.id, text="Введи имя очереди, которую хочешь создать")
    close_connection(con_l, cursor_l)
    bot.register_next_step_handler(message, callback_create_handler)


def callback_create_handler(message):
    try:
        bot.send_message(message.chat.id,
                         text="Введи время в которое нужно занять очередь, которую хочешь создать (например так 20:00)")
        bot.register_next_step_handler(message, callback_create2_handler, message.text)
    except Exception as e:
        print("FUNC: callback_create_handler ERR:", e)


def callback_create2_handler(message, table_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        hour, minute = map(int, message.text.split(':'))
        tables = get_all_tables(con_l, cursor_l)
        if message.text == 'admins' or message.text == 'tables':
            bot.send_message(message.chat.id, text='Самый умный что-ли?')
            return
        for table in tables:
            if table[1] == message.text:
                bot.send_message(message.chat.id, text='Очередь с таким именем уже существует')
                return
        database_init(con_l, cursor_l, table_name)
        insert_table(con_l, cursor_l, {'name': table_name, 'date': dt.now(pytz.timezone('Europe/Minsk')),
                                       'time': dt.strptime(f"{hour}:{minute}", '%H:%M').strftime('%H:%M')})
        bot.send_message(message.chat.id, text=f"Очередь создана")
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_create2_handler ERR:", e)


@bot.message_handler(commands=['admin_delete'])
def handle_delete(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Удаление очереди")
    bot.send_message(message.chat.id, text="Введи имя очереди, которую хочешь удалить")
    bot.register_next_step_handler(message, callback_delete_handler)


def callback_delete_handler(message):
    con_l, cursor_l = database_connect(config['db_name'])
    tables = get_all_tables(con_l, cursor_l)
    exist = False
    if message.text == 'admins' or message.text == 'tables':
        bot.send_message(message.chat.id, text='Самый умный что-ли?')
        return
    for table in tables:
        if table[1] == message.text:
            exist = True
    if not exist:
        bot.send_message(message.chat.id, text='Очередь с таким именем не существует')
        return
    delete_table(con_l, cursor_l, message.text)
    delete_table_from_table(con_l, cursor_l, message.text)
    bot.send_message(message.chat.id, text=f"Очередь с именем {message.text} удалена")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['admin_time'])
def handle_settime(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Изменить время занятия очереди")
    bot.send_message(message.chat.id, text="Введи имя очереди, которую хочешь изменить")
    bot.register_next_step_handler(message, callback_settime_handler)


def callback_settime_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        tables = get_all_tables(con_l, cursor_l)
        exist = False
        no = 0
        if message.text == 'admins' or message.text == 'tables':
            bot.send_message(message.chat.id, text='Самый умный что-ли?')
            return
        for table in tables:
            if table[1] == message.text:
                exist = True
                break
            no += 1
        if not exist:
            bot.send_message(message.chat.id, text='Очередь с таким именем не существует')
            return
        bot.send_message(message.chat.id, text=f"Введи новое время как в примере (20:00)")
        bot.register_next_step_handler(message, callback_settime2_handler, get_table_name(con_l, cursor_l, no + 1))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime_handler ERR:", e)


def callback_settime2_handler(message, table_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        hour, minute = map(int, message.text.split(':'))
        if is_exist_table(con_l, cursor_l, table_name):
            set_table_time(con_l, cursor_l, table_name, dt.strptime(f"{hour}:{minute}", '%H:%M').strftime('%H:%M'))
            bot.send_message(message.chat.id, "Время занятия очереди изменено")
        else:
            print("Нет такой очереди")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime2_handler ERR:", e)


@bot.message_handler(commands=['admin_edit'])
def handle_admin_edit(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Принудительное редактирование очереди")
    bot.send_message(message.chat.id, text="Введи номер очереди, которую хочешь изменить")
    bot.register_next_step_handler(message, callback_admin_edit_handler)


def callback_admin_edit_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Введите номер человека, у которого хочешь изменить имя')
        bot.register_next_step_handler(message, callback_admin_edit2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit_handler ERR:", e)


def callback_admin_edit2_handler(message, db_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, db_name)
        if lst:
            if len(lst) >= int(message.text):
                bot.send_message(message.chat.id, text='Введите имя и фамилию человека')
                bot.register_next_step_handler(message, callback_admin_edit3_handler,
                                               db_name, int(message.text))
            else:
                bot.send_message(message.chat.id, text='Неправильный номер')
        else:
            bot.send_message(message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit2_handler ERR:", e)


def callback_admin_edit3_handler(message, db_name, no):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        update_name(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no, get_table_name(con_l, cursor_l, no))[0][1],
                    message.text, db_name)
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text='Готово')
    except Exception as e:
        print("FUNC: callback_admin_edit3_handler ERR:", e)


@bot.message_handler(commands=['admin_change'])
def handle_admin_change(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Принудительный обмен в очереди")
    bot.send_message(message.chat.id, text="Введи номер очереди, которую хочешь изменить")
    bot.register_next_step_handler(message, callback_admin_change_handler)


def callback_admin_change_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Введи два номера людей через пробел, которых хочешь поменять')
        bot.register_next_step_handler(message, callback_admin_change2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_change_handler ERR:", e)


def callback_admin_change2_handler(message, db_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, db_name)
        no1, no2 = map(int, message.text.split(' '))
        if lst:
            if len(lst) >= no1 and len(lst) >= no2:
                change_queue(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no1, db_name)[0],
                             get_status_by_no(con_l, cursor_l, no2, db_name)[0], db_name)
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
def handle_admin_remove(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Принудительное удаление из очереди")
    bot.send_message(message.chat.id, text="Введи номер очереди, которую хочешь изменить")
    bot.register_next_step_handler(message, callback_admin_remove_handler)


def callback_admin_remove_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Номер человека которого ты хочешь удалить из очереди')
        bot.register_next_step_handler(message, callback_admin_remove2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete_handler ERR:", e)


def callback_admin_remove2_handler(message, db_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, db_name)
        if lst:
            if len(lst) >= int(message.text):
                print(get_status_by_no(con_l, cursor_l, int(message.text), db_name)[0], db_name)
                cancel_take(con_l, cursor_l, get_status_by_no(con_l, cursor_l, int(message.text), db_name)[0][1],
                            db_name)
                bot.send_message(message.chat.id, 'Удалено')
            else:
                bot.send_message(message.chat.id, text='Неправильный номер')
        else:
            bot.send_message(message.chat.id, text='Очередь пуста :(')
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete2_handler ERR:", e)


bot.infinity_polling(skip_pending=True)
