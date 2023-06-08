import time as tm
from telebot import TeleBot
from database import Session, get_all_users, is_admin


class Middleware:
    def __init__(self):
        self.spams: dict = {}
        self.msgs: int = 4
        self.maxim: int = 1
        self.ban: int = 300

    def is_spam(self, bot: TeleBot, user_id: int) -> bool:
        try:
            usr = self.spams[user_id]
            usr["messages"] += 1
        except Exception as e:
            self.spams[user_id] = {"next_time": int(tm.time()) + self.maxim, "messages": 1, "banned": 0}
            usr = self.spams[user_id]
        if usr["banned"] >= int(tm.time()):
            return True
        else:
            if usr["next_time"] >= int(tm.time()):
                if usr["messages"] >= self.msgs:
                    self.spams[user_id]["banned"] = tm.time() + self.ban
                    text = """Хотел поспамить? Получай бан на {} минут""".format(self.ban / 60)
                    bot.send_message(user_id, text)
                    return True
            else:
                self.spams[user_id]["messages"] = 1
                self.spams[user_id]["next_time"] = int(tm.time()) + self.maxim
        return False

    def is_logged(self, bot: TeleBot, session: Session, user_id: int) -> bool:
        try:
            users = get_all_users(session)
            for user in users:
                if str(user[1]) == str(user_id):
                    return True
            bot.send_message(user_id, "Выполните вход в систему /login")
        except Exception as e:
            print("FUNC: callback_login_handler ERR:", e)
        return False

    def is_admin(self, bot: TeleBot, session: Session, user_id: int) -> bool:
        try:
            if not is_admin(session, str(user_id)):
                bot.send_message(user_id, "Недостаточно прав для выполнения этой команды!")
                return False
            else:
                return True
        except Exception as e:
            print("FUNC: is_admin ERR:", e)
            return False
