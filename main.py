import telebot as tt
from datetime import datetime as dt
from database import *
import json
import pytz


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


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id,
                     text='/take - Занять очередь\n/status - Посмотреть какой ты по счету в очереди\n/list - Посмотреть всю очередь\n/change - Поменяться местами с кем-либо\n/cancel - Перехотел сдавать\n/edit - Изменить имя в очереди\n/queues - Посмотреть список очередей\n/time - Посмотреть во сколько нужно занимать')
    con_l, cursor_l = database_connect(config['db_name'])
    if is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id,
                         text='Для админов\n/admin_create - Создать очередь\n/admin_delete - Удалить очередь\n/admin_time - Изменить время занятия очереди\n/admin_edit - Принудительно изменяет имя человека, занявшего очередь\n/admin_delete - Принудительно удаляет человека из очереди\n/admin_change - Принудительно меняет двух человек местами')


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
        hour, minute = map(int, get_table_time(con_l, cursor_l, int(message.text)).split(':'))
        bot.register_next_step_handler(message, callback_take2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)), hour, minute)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_take_handler ERR:", e)


def callback_take2_handler(message, name, hour, minute):
    try:
        time = dt.now(pytz.timezone('Europe/Minsk'))
        con_l, cursor_l = database_connect(config['db_name'])
        if time.hour * 60 + time.minute < hour * 60 + minute:
            bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
            return
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
    except Exception as e:
        bot.send_message(message.chat.id,
                         text='Произошла ошибка, попробуйте снова')
        print("FUNC: callback_take2_handler ERROR:", e)


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
            bot.send_message(message.chat.id,
                             f"{get_status_by_id(con_l, cursor_l, message.chat.id, get_table_name(con_l, cursor_l, int(message.text)))[0][0]}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_status_handler ERR:", e)


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
        print("FUNC: callback_list_handler ERR:", e)


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
        bot.register_next_step_handler(message, callback_change2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_change_handler ERR:", e)


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
        print("FUNC: callback_cancel_handler ERR:", e)


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
        bot.register_next_step_handler(message, callback_edit2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_edit_handler ERR:", e)


def callback_edit2_handler(message, name):
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
    bot.send_message(message.chat.id, 'Введите номер очереди из доступных в /queues')
    bot.register_next_step_handler(message, callback_time_handler)


def callback_time_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        get_table_time(con_l, cursor_l, int(message.text))
        bot.send_message(message.chat.id, text=get_table_time(con_l, cursor_l, int(message.text)))
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
        bot.send_message(message.chat.id, text="Введи время в которое нужно занять очередь, которую хочешь создать (например так 20:00)")
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
        insert_table(con_l, cursor_l, {'name': table_name, 'date': dt.now(pytz.timezone('Europe/Minsk')), 'time': dt.strptime(f"{hour}:{minute}", '%H:%M').strftime('%H:%M')})
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
        update_name(con_l, cursor_l, get_status_by_no(con_l, cursor_l, no, get_table_name(con_l, cursor_l, no))[0][1], message.text, db_name)
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


@bot.message_handler(commands=['admin_delete'])
def handle_admin_delete(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not is_admin(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, text="У тебя недостаточно прав для такой команды")
        return
    bot.send_message(message.chat.id, text="Принудительное удаление из очереди")
    bot.send_message(message.chat.id, text="Введи номер очереди, которую хочешь изменить")
    bot.register_next_step_handler(message, callback_admin_delete_handler)


def callback_admin_delete_handler(message):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        if not is_exist_table(con_l, cursor_l, get_table_name(con_l, cursor_l, int(message.text))):
            close_connection(con_l, cursor_l)
            bot.send_message(message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        bot.send_message(message.chat.id, text=f'Номер человека которого ты хочешь удалить из очереди')
        bot.register_next_step_handler(message, callback_admin_delete2_handler,
                                       get_table_name(con_l, cursor_l, int(message.text)))
        close_connection(con_l, cursor_l)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete_handler ERR:", e)


def callback_admin_delete2_handler(message, db_name):
    try:
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l, db_name)
        if lst:
            if len(lst) >= int(message.text):
                print(get_status_by_no(con_l, cursor_l, int(message.text), db_name)[0], db_name)
                cancel_take(con_l, cursor_l, get_status_by_no(con_l, cursor_l, int(message.text), db_name)[0][1], db_name)
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
