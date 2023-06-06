from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telebot.util import extract_arguments
from database import *
import os
import datetime as dt
import pytz

# todo: move to utils
from bot import help_strings, help_admin_strings


config = {'group': os.getenv('BOT_GROUP')}


def handle_start(session: Session, bot: TeleBot, message: Message):
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id, parse_mode='MarkdownV2', text='`/take` \- _Занять очередь_\n`/status` \- _Посмотреть какой ты по счету в очереди_\n`/list` \- _Посмотреть всю очередь_\n`/change` \- _Поменяться местами с кем\-либо в очереди_\n`/cancel` \- _Перехотел сдавать_\n`/edit` \- _Изменить имя в очереди_\n`/queues` \- _Посмотреть список очередей_\n`/time` \- _Посмотреть во сколько нужно занимать в очереди_\n`/ban` \- _Посмотреть, сколько секунд осталось до разбана_')

    if is_admin(session, str(message.chat.id)):
        bot.send_message(message.chat.id, parse_mode='MarkdownV2', text='_Для админов_\n`/admin_create` \- _Создать очередь_\n`/admin_delete` \- _Удалить очередь_\n`/admin_time` \- _Изменить время занятия очереди_\n`/admin_edit` \- _Принудительно изменяет имя человека, занявшего очередь_\n`/admin_remove` \- _Принудительно удаляет человека из очереди_\n`/admin_change` \- _Принудительно меняет двух человек местами_')
    
    bot.send_message(message.chat.id, text="Напиши `/help имя\_команды`, чтобы узнать о ней подробнее", parse_mode='MarkdownV2')
    bot.send_message(message.chat.id, text="Предупреждаю, в боте стоит антиспам система, если вы начнете спамить вам выдадут бан на 5 минут, если это вас не остановит, вас еще и тг забанит на неопределенное время.")


def login(session: Session, bot: TeleBot, message: Message):
    bot.send_message(message.chat.id, 'Введите номер группы')
    bot.register_next_step_handler(message, callback_login_handler)


def callback_login_handler(session: Session, bot: TeleBot, message: Message):
    try:
        if message.text == config['group']:
            insert_user(session, {"tg_id": message.chat.id,
                                  "username": f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                  "points": 0})
            
            bot.send_message(message.chat.id, 'Вы вошли в систему!')
        else:
            bot.send_message(message.chat.id, text="Понятия не имею, кто ты, герой")
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print("FUNC: callback_login_handler ERR:", e)



def handle_help(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()

    for command in help_strings:
        markup.add(InlineKeyboardButton(f"{command}", callback_data=f"helpbutton {command}"))

    if is_admin(session, str(message.chat.id)):
        for command in help_admin_strings:
            markup.add(InlineKeyboardButton(f"{command}", callback_data=f"helpbutton {command}"))

    bot.send_message(message.chat.id, "Выберите команду", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('helpbutton'))
# def callback_query_help(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     command = call.data[11:]
#     if help_strings.get(command):
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text=help_strings[command], parse_mode="MarkdownV2")
#     elif help_admin_strings.get(command):
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text=help_admin_strings[command], parse_mode="MarkdownV2")
#     else:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text='Такой команды нет')
#         bot.send_message(call.message.chat.id, text='Ознакомьтесь с перечнем команд, написав `/start` или `/help`',
#                          parse_mode='MarkdownV2')


def handle_take(session: Session, bot: TeleBot, message: Message):
    try:
        no = extract_arguments(message.text)
        no = int(no)

        try:
            datetime = get_table_time(session, no).split(' ')
            day, month, year = map(int, datetime[0].split('-'))
            hour, minute = map(int, datetime[1].split(':'))

            time = dt.now(pytz.timezone('Europe/Minsk'))
            time = time.replace(tzinfo=None)

            if time < dt.strptime(f'{day}-{month}-{year} {hour}:{minute}', '%d-%m-%Y %H:%M'):
                bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
                return
            
            table_name = get_table_name(session, int(no))
            lst = get_all(session, table_name)
            
            if lst is not None:
                for human in lst:
                    if human[1] == str(message.chat.id):
                        bot.send_message(message.chat.id, text=f'Вы уже заняли очередь')
                        return

            time_s = time.strftime("%H:%M:%S:%f")
            
            insert_value(session, {'tg_id': message.chat.id, 
                                   'time': time,
                                   'username': f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                   'change': -1}, table_name)
            
            bot.send_message(message.chat.id, text=f'Время получения запроса: {time_s}')
            bot.send_message(message.chat.id, text=f'Вы заняли очередь в {get_table_name(session, no)}')
        except Exception as e:
            bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
            print("FUNC: callback_take_handler ERR:", e)
    except Exception as e:
        markup = InlineKeyboardMarkup()
        tables = get_all_tables(session)

        idx = 1

        if not tables:
            bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
            return
        
        for table in tables:
            markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"takebutton {idx}"))
            idx += 1

        bot.send_message(message.chat.id, "Занять очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('takebutton'))
# def callback_query_take(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         session = database_connect(config['db_name'])
#         no = int(call.data[11:])
#         datetime = get_table_time(session, no).split(' ')
#         day, month, year = map(int, datetime[0].split('-'))
#         hour, minute = map(int, datetime[1].split(':'))
#         time = dt.now(pytz.timezone('Europe/Minsk'))
#         time = time.replace(tzinfo=None)
#         if time < dt.strptime(f'{day}-{month}-{year} {hour}:{minute}', '%d-%m-%Y %H:%M'):
#             bot.send_message(call.message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             return
#         table_name = get_table_name(session, int(no))
#         lst = get_all(session, table_name)
#         if lst is not None:
#             for human in lst:
#                 if human[1] == str(call.message.chat.id):
#                     close_connection(session)
#                     bot.send_message(call.message.chat.id, text=f'Вы уже заняли очередь')
#                     bot.delete_message(call.message.chat.id, call.message.message_id)
#                     return
#         time_s = time.strftime("%H:%M:%S:%f")
#         insert_value(session, {'tg_id': call.message.chat.id, 'time': time,
#                                        'username': f"{call.message.chat.first_name if call.message.chat.first_name is not None else ''} {call.message.chat.last_name if call.message.chat.last_name is not None else ''}",
#                                        'change': -1}, table_name)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id,
#                          text=f'Вы заняли очередь в {get_table_name(session, no)}\nВремя: {time_s}')
#         close_connection(session)
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_take_handler ERR:", e)


def handle_status(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1

    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"statusbutton {idx}"))
        idx += 1

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('statusbutton'))
# def callback_query_status(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[13:])
#         session = database_connect(config['db_name'])
#         if not is_exist_table(session, get_table_name(session, no)):
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
#             return
#         if not get_status_by_id(session, str(call.message.chat.id), get_table_name(session, no)):
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
#         else:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              f"Вы {get_status_by_id(session, str(call.message.chat.id), get_table_name(session, no))[0][0]} в очереди {get_table_name(session, no)}")
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_status_handler ERR:", e)


def handle_list(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1
    
    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"listbutton {idx}"))
        idx += 1

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('listbutton'))
# def callback_query_list(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[11:])
#         session = database_connect(config['db_name'])
#         if not is_exist_table(session, get_table_name(session, no)):
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
#             return
#         lst = get_all_in_order(session, get_table_name(session, no))
#         if not lst:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, text="Никто не занял очередь :(")
#             close_connection(session)
#             return
#         else:
#             s = f"Очередь {get_table_name(session, no)}:\n"
#             for human in lst:
#                 s += f"№{str(human[0])} {str(human[2])} Время: {str(human[3])}\n"
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, text=s)
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_list_handler ERR:", e)


def handle_change(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1

    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"changebutton {idx}"))
        idx += 1

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('changebutton'))
# def callback_query_change(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[13:])
#         session = database_connect(config['db_name'])
#         if not is_exist_table(session, get_table_name(session, no)):
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
#             return
#         lst = get_all(session, get_table_name(session, no))
#         exist = False
#         for human in lst:
#             if human[1] == str(call.message.chat.id):
#                 exist = True
#         if not exist:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, text=f'Ты не занял очередь :(')
#             return
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         markup = InlineKeyboardMarkup()
#         idx = 1
#         for human in lst:
#             markup.add(InlineKeyboardButton(f"№{human[0]} {human[2]}",
#                                                      callback_data=f"change2button {human[0]} {get_table_name(session, no)}"))
#             idx += 1
#         bot.send_message(call.message.chat.id, "Выбери человека", reply_markup=markup)
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_change_handler ERR:", e)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('change2button'))
# def callback_change_handler(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     no: int
#     try:
#         data = call.data.split(' ')
#         no = int(data[1])
#         table_name = data[2]
#         session = database_connect(config['db_name'])
#         lst = get_all(session, table_name)
#         if not lst:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, text="Никто не занял очередь :(")
#             return
#         if len(lst) < no:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, text="Такого номера не существует")
#             return
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Запрос на изменение очереди принят')
#         update_change(session, get_status_by_id(session, str(call.message.chat.id), table_name)[0], no,
#                       table_name)
#         if lst[no - 1][4] == get_status_by_id(session, str(call.message.chat.id), table_name)[0][0] != -1:
#             bot.send_message(get_status_by_no(session, no, table_name)[0][1],
#                              text=f"{get_status_by_id(session, str(call.message.chat.id), table_name)[0][2]} поменялся с тобой (№{get_status_by_id(session, str(call.message.chat.id), table_name)[0][0]})")
#             change_queue(session, get_status_by_id(session, str(call.message.chat.id), table_name)[0],
#                          get_status_by_no(session, no, table_name)[0], table_name)
#             bot.send_message(call.message.chat.id, 'Очередь изменена')
#         else:
#             bot.send_message(get_status_by_no(session, no, table_name)[0][1],
#                              text=f"{get_status_by_id(session, str(call.message.chat.id), table_name)[0][2]} хочет с тобой поменяться (№{get_status_by_id(session, str(call.message.chat.id), table_name)[0][0]})")
#             bot.send_message(call.message.chat.id,
#                              'Второй человек тоже должен поменяться с тобой местом чтобы очередь изменилась')
#         close_connection(session)

#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         print("FUNC: callback_change2_handler ERR:", e)
#         bot.send_message(call.message.chat.id, 'Такого номера не существует')


def handle_cancel(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1

    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"cancelbutton {idx}"))
        idx += 1
    
    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('cancelbutton'))
# def callback_query_cancel(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[13:])
#         session = database_connect(config['db_name'])
#         if not is_exist_table(session, get_table_name(session, no)):
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
#             return
#         if not get_status_by_id(session, str(call.message.chat.id), get_table_name(session, no)):
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
#             return
#         cancel_take(session, str(call.message.chat.id), get_table_name(session, no))
#         close_connection(session)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text='Ты освободил свое место в очереди')
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_cancel_handler ERR:", e)


def handle_edit(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1

    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"editbutton {idx}"))
        idx += 1

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('editbutton'))
# def callback_query_edit(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[11:])
#         session = database_connect(config['db_name'])
#         if not is_exist_table(session, get_table_name(session, no)):
#             close_connection(session)
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id,
#                              text=f'Такой очереди нет, посмотрите список доступных очередей в /queues')
#             return
#         if not get_status_by_id(session, str(call.message.chat.id), get_table_name(session, no)):
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             bot.send_message(call.message.chat.id, f"Вы не заняли очередь :(")
#             return
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text='Напиши имя и фамилию')
#         bot.register_next_step_handler(call.message, callback_edit_handler,
#                                        get_table_name(session, no))
#         close_connection(session)
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_edit_handler ERR:", e)


def callback_edit_handler(session: Session, bot: TeleBot, message: Message, table_name: str):
    try:
        update_name(session, str(message.chat.id), message.text, table_name)
        bot.send_message(message.chat.id, text='Готово')
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
        print(e)


def handle_queues(session: Session, bot: TeleBot, message: Message):
    tables = get_all_tables(session)
    
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


def handle_time(session: Session, bot: TeleBot, message: Message):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    idx = 1
    
    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Если скоро сдавать напишите админам, чтобы добавили очередь")
        return
    
    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"timebutton {idx}"))
        idx += 1

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
    close_connection(session)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('timebutton'))
# def callback_query_time(call: CallbackQuery):
#     if is_spam(call.message.chat.id):
#         return
#     try:
#         no = int(call.data[11:])
#         session = database_connect(config['db_name'])
#         get_table_time(session, no)
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, text=get_table_time(session, no))
#     except Exception as e:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.send_message(call.message.chat.id, 'Что-то не так с вводом, попробуй еще раз')
#         print("FUNC: callback_time_handler ERR:", e)


# def handle_ban(session: Session, bot: TeleBot, message: Message):
#     if is_spam(message.chat.id):
#         bot.send_message(message.chat.id,
#                          text=f"{int(spams[message.chat.id]['banned'] - int(tm.time()))} секунд осталось до разбана")
#         return
#     elif not is_logged(message.chat.id):
#         return
#     else:
#         bot.send_message(message.chat.id, text="Вы не забанены")
