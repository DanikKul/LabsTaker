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

# Initialize database
con, cursor = database_connect(config['db_name'])
cursor.execute("DROP TABLE IF EXISTS 'queue'")
database_init(con, cursor)
close_connection(con, cursor)


# __________________________________________TELEGRAM BOT HANDLERS_____________________________________________________ #


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, text='Привет')
    bot.send_message(message.chat.id, text='Вот все команды, которые ты можешь использовать')
    bot.send_message(message.chat.id,
                     text='/take - Занять очередь\n/status - Посмотреть какой ты по счету в очереди\n/list - Посмотреть всю очередь\n/change - Поменяться местами с кем-либо\n/cancel - Перехотел сдавать\n/edit - Изменить имя в очереди')


@bot.message_handler(commands=['take'])
def handle_take(message):
    time = dt.now()
    con_l, cursor_l = database_connect(config['db_name'])
    # if time.hour < 22 or time.minute < 39:
    #     bot.send_message(message.chat.id, f"Слишком рано: {time.strftime('%H:%M:%S:%f')}")
    #     return
    lst = get_all(con_l, cursor_l)
    if lst is not None:
        for human in lst:
            if human[1] == str(message.chat.id):
                close_connection(con_l, cursor_l)
                bot.send_message(message.chat.id, text=f'Вы уже заняли очередь')
                return
    time_s = time.strftime("%H:%M:%S:%f")
    insert_value(con_l, cursor_l, {'tg_id': message.chat.id, 'time': time_s,
                                   'username': f"{message.from_user.first_name if message.from_user.first_name is not None else ''} {message.from_user.last_name if message.from_user.last_name is not None else ''}",
                                   'change': -1})
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id,
                     text=f'Время получения запроса: {time_s}')


@bot.message_handler(commands=['status'])
def handle_status(message):
    con_l, cursor_l = database_connect(config['db_name'])
    if not get_status_by_id(con_l, cursor_l, message.chat.id):
        bot.send_message(message.chat.id, f"Никто не занял очередь :(")
    else:
        bot.send_message(message.chat.id, f"{get_status_by_id(con_l, cursor_l, message.chat.id)[0][0]}")


@bot.message_handler(commands=['list'])
def handle_list(message):
    con_l, cursor_l = database_connect(config['db_name'])
    lst = get_all(con_l, cursor_l)
    if not lst:
        bot.send_message(message.chat.id, text="Никто не занял очередь :(")
    else:
        s = ""
        for human in lst:
            s += f"№{str(human[0])} {str(human[2])} Время: {str(human[3])}\n"
        close_connection(con_l, cursor_l)
        bot.send_message(message.chat.id, text=s)


@bot.message_handler(commands=['change'])
def handle_change(message):
    bot.send_message(message.chat.id, text='Введите номер в очереди с которым хотите поменяться')
    bot.register_next_step_handler(message, callback_handler)


def callback_handler(message):
    no: int
    try:
        no = int(message.text)
        con_l, cursor_l = database_connect(config['db_name'])
        lst = get_all(con_l, cursor_l)
        if not lst:
            bot.send_message(message.chat.id, text="Никто не занял очередь :(")
            return
        if len(lst) < no:
            bot.send_message(message.chat.id, text="Такого номера не существует")
            return
        bot.send_message(message.chat.id, 'Запрос на изменение очереди принят')
        update_change(con_l, cursor_l, get_status_by_id(con_l, cursor_l, message.chat.id)[0], no)
        if lst[no - 1][4] == get_status_by_id(con_l, cursor_l, message.chat.id)[0][0] != -1:
            print(get_status_by_id(con_l, cursor_l, message.chat.id))
            print(get_status_by_no(con_l, cursor_l, no))
            change_queue(con_l, cursor_l, get_status_by_id(con_l, cursor_l, message.chat.id)[0], get_status_by_no(con_l, cursor_l, no)[0])
            bot.send_message(message.chat.id, 'Очередь изменена')
        else:
            bot.send_message(message.chat.id,
                             'Второй человек тоже должен поменяться с тобой местом чтобы очередь изменилась')
        close_connection(con_l, cursor_l)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Такого номера не существует')


@bot.message_handler(commands=['cancel'])
def handle_change(message):
    con_l, cursor_l = database_connect(config['db_name'])
    cancel_take(con_l, cursor_l, message.chat.id)
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id, text='Ты освободил свое место в очереди')


@bot.message_handler(commands=['edit'])
def handle_change(message):
    bot.send_message(message.chat.id, text='Напиши имя и фамилию')
    bot.register_next_step_handler(message, callback_edit_handler)


def callback_edit_handler(message):
    con_l, cursor_l = database_connect(config['db_name'])
    update_name(con_l, cursor_l, message.chat.id, message.text)
    close_connection(con_l, cursor_l)
    bot.send_message(message.chat.id, text='Готово')


bot.infinity_polling(timeout=1000, skip_pending=True, long_polling_timeout=1000)
