from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database import *
from datetime import datetime as dt
import pytz
from configuration import get_config
from utils import add_queue_keyboard

config = get_config()
tg_bot = tg_bot


def admin_create_hd(session: Session, bot: TeleBot, message: Message):
    bot.send_message(message.chat.id, text="Создание очереди")
    bot.send_message(message.chat.id, text="Введи имя очереди, которую хочешь создать")
    bot.register_next_step_handler(message, callback_admin_create_hd_a)


def callback_admin_create_hd_a(session: Session, bot: TeleBot, message: Message):
    try:
        bot.send_message(message.chat.id,
                         text="Введи время в которое нужно занять очередь, которую хочешь создать (DD-MM HH:MM)")
        bot.register_next_step_handler(message, callback_admin_create_hd_b, message.text)
    except Exception as e:
        print("FUNC: callback_create_handler ERR:", e)


def callback_admin_create_hd_b(session: Session, bot: TeleBot, message: Message, table_name: str):
    try:
        datetime = message.text.split(' ')
        day, month = map(int, datetime[0].split('-'))
        hour, minute = map(int, datetime[1].split(':'))

        tables = get_all_tables(session)

        if message.text == 'admins' or message.text == 'tables' or message.text == 'users':
            bot.send_message(message.chat.id, text='Самый умный что-ли?')
            return

        for table in tables:
            if table[1] == message.text:
                bot.send_message(message.chat.id, text='Очередь с таким именем уже существует')
                return

        database_init(session, table_name)
        insert_table(session, {'name': table_name,
                               'date': dt.now(pytz.timezone('Europe/Minsk')),
                               'time': dt.strptime(f"{day}-{month}-{dt.now(pytz.timezone('Europe/Minsk')).year} {hour}:{minute}", '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M')})

        bot.send_message(message.chat.id, text=f"Очередь создана")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_create2_handler ERR:", e)


def admin_delete_hd(session: Session, bot: TeleBot, message: Message):
    add_queue_keyboard(session, bot, message, 'admindeletebutton')


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admindeletebutton'))
def callback_query_admin_delete_hd(call: CallbackQuery):
    table_name = call.data[18:]
    session = database_connect(config['db_name'])
    tables = get_all_tables(session)
    exist = False
    if table_name == 'admins' or table_name == 'tables' or table_name == 'users':
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, text='Самый умный что-ли?')
        return
    for table in tables:
        if table[1] == table_name:
            exist = True
    if not exist:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, text='Очередь с таким именем не существует')
        return
    delete_table(session, table_name)
    delete_table_from_table(session, table_name)
    tg_bot.delete_message(call.message.chat.id, call.message.message_id)
    tg_bot.send_message(call.message.chat.id, text=f"Очередь с именем {table_name} удалена")
    close_connection(session)


def admin_time_hd(session: Session, bot: TeleBot, message: Message):
    add_queue_keyboard(session, bot, message, 'admintimebutton')


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admintimebutton'))
def callback_query_admin_time_hd(call: CallbackQuery):
    try:
        table_name = call.data[16:]
        session = database_connect(config['db_name'])
        tables = get_all_tables(session)
        exist = False
        no = 0
        if table_name == 'admins' or table_name == 'tables' or table_name == 'users':
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text='Самый умный что-ли?')
            return
        for table in tables:
            if table[1] == table_name:
                exist = True
                break
            no += 1
        if not exist:
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text='Очередь с таким именем не существует')
            return
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, text=f"Введи новое время как в примере (DD-MM HH:MM)")
        tg_bot.register_next_step_handler(call.message, callback_admin_time_hd, get_table_name(session, no + 1))
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime_handler ERR:", e)


def callback_admin_time_hd(session: Session, bot: TeleBot, message: Message, table_name: str):
    try:
        datetime = message.text.split(' ')
        day, month = map(int, datetime[0].split('-'))
        hour, minute = map(int, datetime[1].split(':'))

        if is_exist_table(session, table_name):
            set_table_time(session, table_name,
                           dt.strptime(f"{day}-{month}-{dt.now(pytz.timezone('Europe/Minsk')).year} {hour}:{minute}", '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M'))

            bot.send_message(message.chat.id, "Время занятия очереди изменено")
        else:
            print("Нет такой очереди")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_settime2_handler ERR:", e)


def admin_edit_hd(session: Session, bot: TeleBot, message: Message):
    add_queue_keyboard(session, bot, message, 'admineditbutton')


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('admineditbutton'))
def callback_query_admin_edit_hd_a(call: CallbackQuery):
    try:
        table_name = call.data[16:]
        session = database_connect(config['db_name'])
        if not is_exist_table(session, table_name):
            close_connection(session)
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        markup = InlineKeyboardMarkup()
        lst = get_all(session, table_name)
        if lst:
            for human in lst:
                markup.add(InlineKeyboardButton(f"{human[2]}", callback_data=f"adminedit2button {human[0]} {table_name}"))
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
        else:
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit_handler ERR:", e)


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminedit2button'))
def callback_query_admin_edit_hd_b(call: CallbackQuery):
    try:
        data = call.data.split(' ')
        db_id = int(data[1])
        table_name = data[2]
        session = database_connect(config['db_name'])
        lst = get_all(session, table_name)
        if lst:
            if len(lst) >= db_id:
                tg_bot.delete_message(call.message.chat.id, call.message.message_id)
                tg_bot.send_message(call.message.chat.id, text='Введите имя и фамилию человека')
                tg_bot.register_next_step_handler(call.message, callback_admin_edit_hd, table_name, db_id)
            else:
                tg_bot.delete_message(call.message.chat.id, call.message.message_id)
                tg_bot.send_message(call.message.chat.id, text='Неправильный номер')
        else:
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_edit2_handler ERR:", e)


def callback_admin_edit_hd(session: Session, bot: TeleBot, message: Message, table_name: str, no: int):
    try:
        update_name(session,
                    get_status_by_no(session, no, table_name)[0][1],
                    message.text, table_name)

        bot.send_message(message.chat.id, text='Готово')
    except Exception as e:
        print("FUNC: callback_admin_edit3_handler ERR:", e)


def admin_change_hd(session: Session, bot: TeleBot, message: Message):
    add_queue_keyboard(session, bot, message, 'adminchangebutton')


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminchangebutton'))
def callback_query_admin_change_hd(call: CallbackQuery):
    try:
        table_name = call.data[18:]
        session = database_connect(config['db_name'])
        if not is_exist_table(session, table_name):
            close_connection(session)
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, text=f'Введи два номера людей через пробел, которых хочешь поменять')
        tg_bot.register_next_step_handler(call.message, callback_admin_change_hd, table_name)
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_change_handler ERR:", e)


def callback_admin_change_hd(session: Session, bot: TeleBot, message: Message, table_name: str):
    try:
        lst = get_all(session, table_name)
        no1, no2 = map(int, message.text.split(' '))

        if lst:
            if len(lst) >= no1 and len(lst) >= no2:
                change_queue(session,
                             get_status_by_no(session, no1, table_name)[0],
                             get_status_by_no(session, no2, table_name)[0], table_name)

                bot.send_message(message.chat.id, 'Очередь изменена')
            else:
                bot.send_message(message.chat.id, text='Неправильный номер')
        else:
            bot.send_message(message.chat.id, text='Очередь пуста :(')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_change2_handler ERR:", e)


def admin_remove_hd(session: Session, bot: TeleBot, message: Message):
    add_queue_keyboard(session, bot, message, 'adminremovebutton')


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminremovebutton'))
def callback_query_admin_remove_hd_a(call: CallbackQuery):
    try:
        table_name = call.data[18:]
        session = database_connect(config['db_name'])
        if not is_exist_table(session, table_name):
            close_connection(session)
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
            return
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = InlineKeyboardMarkup()
        lst = get_all(session, table_name)
        for human in lst:
            markup.add(InlineKeyboardButton(f"№{human[0]} {human[2]}", callback_data=f"adminremove2button {human[0]} {table_name}"))
        tg_bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete_handler ERR:", e)


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminremove2button'))
def callback_query_admin_remove_hd_b(call: CallbackQuery):
    try:
        data = call.data.split(' ')
        no = int(data[1])
        table_name = data[2]
        session = database_connect(config['db_name'])
        lst = get_all(session, table_name)
        if lst:
            if len(lst) >= no:
                cancel_take(session, get_status_by_no(session, no, table_name)[0][1], table_name)
                tg_bot.delete_message(call.message.chat.id, call.message.message_id)
                tg_bot.send_message(call.message.chat.id, 'Удалено')
            else:
                tg_bot.delete_message(call.message.chat.id, call.message.message_id)
                tg_bot.send_message(call.message.chat.id, text='Неправильный номер')
        else:
            tg_bot.delete_message(call.message.chat.id, call.message.message_id)
            tg_bot.send_message(call.message.chat.id, text='Очередь пуста :(')
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete2_handler ERR:", e)


def admin_list_hd(session: Session, bot: TeleBot, message: Message):
    admins = get_all_admins(session)
    if not admins:
        bot.send_message(message.chat.id, text="Нет ни одного админа")
        return

    s = "Администраторы:\n"
    for admin in admins:
        s += f"{admin[2]}\n"

    bot.send_message(message.chat.id, text=s)


def admin_kick_hd(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    users = get_all_users(session)

    if not users:
        bot.send_message(message.chat.id, text="Нет ни одного пользователя")
        return

    for human in users:
        markup.add(InlineKeyboardButton(f"{human[2]}", callback_data=f"adminkickbutton {human[1]}"))

    bot.send_message(message.chat.id, "Выбери пользователя", reply_markup=markup)


@tg_bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('adminkickbutton'))
def callback_query_admin_kick_hd(call: CallbackQuery):
    try:
        data = call.data.split(' ')
        tg_id = data[1]
        session = database_connect(config['db_name'])
        remove_admin(session, tg_id)
        remove_user(session, tg_id)
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Пользователь удален')
        close_connection(session)
    except Exception as e:
        tg_bot.delete_message(call.message.chat.id, call.message.message_id)
        tg_bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_admin_delete2_handler ERR:", e)


def admin_users_hd(session: Session, bot: TeleBot, message: Message):
    users = get_all_users(session)

    if not users:
        bot.send_message(message.chat.id, text="Нет ни одного пользователя")
        return

    s = "Пользователи:\n"
    for human in users:
        s += f"{human[2]}, приоритет: {human[3]}\n"

    bot.send_message(message.chat.id, text=s)
