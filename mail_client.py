import re
import socket
import uuid
import psutil

import config
import smtplib
from datetime import datetime


class MailClient:
    def __init__(self):
        try:
            self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.server.ehlo()
            self.server.login(config.rpi_mail, config.rpi_mail_password)
        except Exception as e:
            print("Something went wrong with MailClient: {}".format(e))

    def send_mail_raport(self):
        ip = socket.gethostbyname(socket.gethostname())
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        cpu_percentage_usage = psutil.cpu_percent(3)
        free_memory = int(psutil.virtual_memory()[3] / 1024 / 1024)

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H:%M")
        subject = "{} StravaBot raport".format(dt_string)

        try:
            with open(config.logfile) as f:
                log_content = f.read()
        except FileNotFoundError as e:
            print(f"\nerror :: {e}")
            log_content = e

        body = \
            "IP: {}\nMAC: {}\nCPU percentage usage: {}\n" \
            "Free memory: {} MB\n\n Logs:\n{}" \
            .format(ip, mac, cpu_percentage_usage, free_memory,
                    log_content)

        email_text = "From: {}\nTo: {}\nSubject: {}\n\n{}" \
            .format(config.rpi_mail, config.email, subject, body)

        self.server.sendmail(config.rpi_mail, config.email, email_text)

    def close(self):
        self.server.close()

