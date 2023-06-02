import telebot as tt
from datetime import datetime as dt
from database import *
import json

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


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id,
                     text='/take - Занять очередь\n/status - Посмотреть какой ты по счету в очереди\n/list - Посмотреть всю очередь\n/change - Поменяться местами с кем-либо\n/cancel - Перехотел сдавать\n/edit - Изменить имя в очереди\n/queues - Посмотреть список очередей')
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id,
                         text='Для админов\n/create - создать очередь\n/delete - удалить очередь')


@bot.message_handler(commands=['take'])
def handle_take(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_take_handler)


def callback_take_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text="Для того чтобы занять очередь, напишите любое сообщение")
        bot.register_next_step_handler(message, callback_take2_handler, get_table_name(con_l, cursor_l, int(message.text)))
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


def callback_take2_handler(message, name):
    time = dt.now()
    con_l, cursor_l = database_connect(config['db_name'])
    # if time.hour < 22 or time.minute < 39:
    #     bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
    #     return
    lst = get_all(con_l, cursor_l, name)
    if lst is not None:
        for human in lst:
            if human[1] == str(message.chat.id):
                close_connection(con_l, cursor_l)
                bot.send_message(message.chat.id, text=f'Вы уже заняли очередь')
                return
    time_s = time.strftime("%H:%M:%S:%f")
    insert_value(con_l, cursor_l, {'tg_id': message.chat.id, 'time': time_s,
                                   'username': f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                   'change': -1}, name)
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id,
                     text=f'Время получения запроса: {time_s}')


@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_status_handler)


def callback_status_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        if not get_status_by_id(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, int(message.text))):
            bot.send_message(message.chat.id, f"Никто не занял очередь :(")
        else:
            bot.send_message(message.chat.id, f"{get_status_by_id(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, int(message.text)))[0][0]}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


@bot.message_handler(commands=['list'])
def handle_list(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_list_handler)


def callback_list_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        lst = get_all(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text)))
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
        print(e)


@bot.message_handler(commands=['change'])
def handle_change(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_change_handler)


def callback_change_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Введите номер человека с которым хотите поменяться')
        bot.register_next_step_handler(message, callback_change2_handler, get_table_name(con_l, cursor_l, int(message.text)))
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


def callback_change2_handler(message, name):
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
            change_queue(con_l, cursor_l, get_status_by_id(con_l, cursor_l, message.chat.id, name)[0], get_status_by_no(con_l, cursor_l, no, name)[0], name)
            bot.send_message(message.chat.id, 'Очередь изменена')
        else:
            bot.send_message(message.chat.id,
                             'Второй человек тоже должен поменяться с тобой местом чтобы очередь изменилась')
        close_connection(con_l, cursor_l)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Такого номера не существует')


@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_cancel_handler)


def callback_cancel_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        cancel_take(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text='Ты освободил свое место в очереди')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)

@bot.message_handler(commands=['edit'])
def handle_edit(message):
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_edit_handler)


def callback_edit_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text='Напиши имя и фамилию')
        bot.register_next_step_handler(message, callback_edit2_handler, get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


def callback_edit2_handler(message, name):
    con_l, cursor_l = database_connect(config['db_name'])
    update_name(con_l, cursor_l, message.chat.id, message.text, name)
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id, text='Готово')


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
    make_admin(con_l, cursor_l, {"tg_id": message.chat.id, "username": f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}"})
    bot.send_message(message.chat.id, text="Ты админ")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['create'])
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
    con_l, cursor_l = database_connect(config['db_name'])
    tables = get_all_tables(con_l, cursor_l)
    if message.text == 'admins' or message.text == 'tables':
        bot.send_message(message.chat.id, text='Самый умный что-ли?')
        return
    for table in tables:
        if table[1] == message.text:
            bot.send_message(message.chat.id, text='Очередь с таким именем уже существует')
            return
    database_init(con_l, cursor_l, message.text)
    insert_table(con_l, cursor_l, {'name': message.text, 'date': dt.now()})
    bot.send_message(message.chat.id, text=f"Очередь с именем {message.text} создана")
    close_connection(con_l, cursor_l)


@bot.message_handler(commands=['delete'])
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


bot.infinity_polling(timeout=1000, skip_pending=True, long_polling_timeout=1000)
