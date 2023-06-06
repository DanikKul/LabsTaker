from database import Session, get_all_tables
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot


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

def add_queue_keyboard(session: Session, bot: TeleBot, message: Message, callback_data: str):
    markup = InlineKeyboardMarkup()
    tables = get_all_tables(session)

    if not tables:
        bot.send_message(message.chat.id, text="Нет ни одной очереди. Создай хотя бы одну")
        return

    for table in tables:
        markup.add(InlineKeyboardButton(f"{table[1]}", callback_data=f"{callback_data} {table[1]}"))

    bot.send_message(message.chat.id, "Выберите очередь", reply_markup=markup)
