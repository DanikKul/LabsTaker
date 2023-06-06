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

config = {'db_name': os.getenv('BOT_LOCAL_DB_NAME') if os.getenv('BOT_ENV') == 'local' else os.getenv('BOT_DOCKER_DB_NAME'),
          'token': os.getenv('BOT_TOKEN'),
          'db_admin': os.getenv('BOT_DB_ADMIN'),
          'db_tables': os.getenv('BOT_DB_TABLES'),
          'group': os.getenv('BOT_GROUP'),
          'pass': os.getenv('BOT_PASS')}

bot = tt.TeleBot(token=config['token'], parse_mode=None, num_threads=6)

session = database_connect(config['db_name'])

db_init_admin(session)
tables_database_init(session)
db_init_users(session)
close_connection(session)

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
        session = database_connect(config['db_name'])
        users = get_all_users(session)
        for user in users:
            if str(user[1]) == str(user_id):
                return True
        close_connection(session)
        bot.send_message(user_id, "Выполните вход в систему /login")
    except Exception as e:
        print("FUNC: callback_login_handler ERR:", e)
    return False


# __________________________________________TELEGRAM BOT HANDLERS_____________________________________________________ #

# __________________________________________USER COMMANDS HANDLERS____________________________________________________ #


user_cmd = {'start' : start_hd, 
            'login' : login_hd, 
            'help' : help_hd, 
            'su' : su_hd, 
            'take' : take_hd, 
            'status' : status_hd, 
            'list' : list_hd, 
            'exchange' : exchange_hd, 
            'cancel' : cancel_hd, 
            'edit' : edit_hd, 
            'time' : time_hd, 
            'queues' : queues_hd, 
            'ban' : ban_hd}

sudo_cmd = {'admin_create' : admin_create_hd, 
            'admin_delete' : admin_delete_hd, 
            'admin_remove' : admin_remove_hd, 
            'admin_edit' : admin_edit_hd, 
            'admin_change' : admin_change_hd, 
            'admin_time' : admin_time_hd, 
            'admin_users' : admin_users_hd, 
            'admin_kick' : admin_kick_hd, 
            'admin_list' : admin_list_hd}


def message_filter(id: int) -> bool:
    if is_spam(id):
        return False

    if not is_logged(id):
        return False

    return True


@bot.message_handler(regexp=r'/([a-zA-Z_])+')
def command_hd(command: tt.types.Message):
    if not message_filter(command.chat.id):
        return
    
    hd = user_cmd.get(command.text)
    
    if hd is not None:
        # command has been found
        return
        
    hd = sudo_cmd.get(command.text)

    if hd is not None:
        # command has been found
        if not is_admin(session, command.chat.id):
            # user is not su
            return 
    
        # todo: stuff
        return

    # command not found    
    return


@bot.message_handler()
def message_hd(message: tt.types.Message):
    message_filter(message.chat.id)    

def start():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    start()
