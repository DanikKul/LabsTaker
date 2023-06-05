from datetime import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psutil
import time
import pytz
import os

smtp_server = "smtp.gmail.com"
port = 587
sender_email = os.getenv("BOT_EMAIL")
receiver_emails = [
    "kulakovich2@gmail.com",
    "sasha@gravity-production.by"
]
password = os.getenv("BOT_EMAIL_PASS")


context = ssl.create_default_context()


def is_online():
    exist = False
    for proc in psutil.process_iter():
        print(proc.name(), proc.cmdline())
        try:
            if proc.cmdline()[-1].endswith('bot.py'):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return exist


def send(receiver):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver
    message['Subject'] = 'Бот умер'
    message.attach(MIMEText(f"Бот лег иди спасать: Время: {datetime.now(pytz.timezone('Europe/Minsk'))}", 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.ehlo()
    session.login(sender_email, password)
    text = message.as_string()
    session.sendmail(sender_email, receiver, text)
    session.quit()


if __name__ == "__main__":
    time.sleep(10)
    while True:
        if not is_online():
            for r in receiver_emails:
                send(r)
            print("BOT OFFLINE")
            break
        time.sleep(60)
