import logging
import random
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import config
from mail_client import MailClient

TIME_STRAVA_LOGGING = 15
TIME_STRAVA_REFRESH = 15
BYTES_IN_KB = 1024


class KudosBot:
    def __init__(self):
        log_formatter = logging.Formatter(
            fmt='%(asctime)s :: %(levelname)s :: %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S')
        self.handler = RotatingFileHandler(
            config.logfile, mode='a', maxBytes=BYTES_IN_KB * config.logfile_size_in_kb,
            backupCount=1, encoding=None, delay=0)
        self.handler.setFormatter(log_formatter)
        self.handler.setLevel(logging.INFO)

        self.logger = logging.getLogger('root')
        self.logger.setLevel(logging.INFO)

        self.logger.addHandler(self.handler)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path=config.driver_path, options=options)
        self.login()

        try:
            self.enable_bot()
        except Exception as e:
            print(f"error :: {e} | Emergency disabling bot...")
        finally:
            self.disable_bot()

    def login(self):
        self.driver.get("https://www.strava.com/login")
        self.sleep(TIME_STRAVA_LOGGING)

        mail = self.driver.find_element_by_css_selector("input[type='email']")
        mail.send_keys(config.email)

        password = self.driver.find_element_by_css_selector("input[type='password']")
        password.send_keys(config.password)
        password.send_keys(Keys.RETURN)
        self.sleep(TIME_STRAVA_LOGGING)

    def go_to_club_recent_activities(self, club_name):
        if club_name.lower() == "following":
            self.driver.get(f"https://www.strava.com/dashboard?feed_type=following")
        else:
            self.driver.get(f"https://www.strava.com/clubs/{club_name}/recent_activity")
        self.sleep(TIME_STRAVA_REFRESH)

    def enable_bot(self, clubs_number=5):
        self.log_current_time()

        selected_clubs = random.choices(config.club_list, k=clubs_number)

        for club in selected_clubs:
            club_kudos = 0
            kudos_limit = random.randint(10, 16)
            self.go_to_club_recent_activities(club_name=club)

            unfilled_kudos = self.driver.find_elements_by_xpath(
                '//*[@data-testid="unfilled_kudos"]')

            new_kudos_quantity = 0

            for kudos_button in unfilled_kudos:
                try:
                    kudos_button.click()
                except Exception as e:
                    print(f"error :: {e}")
                    break
                new_kudos_quantity += 1
                club_kudos += 1

                if new_kudos_quantity >= kudos_limit:
                    break
                self.sleep(random.randint(30, 65))

            print(f"info :: Club: {club} | Kudos: {club_kudos}")
            self.logger.info(f"{club} | Kudos: {club_kudos}")

    def sleep(self, sleep_time, verbose=False):
        if verbose:
            print(f"info :: Sleeping for: {sleep_time} seconds...")
        time.sleep(sleep_time)

    def disable_bot(self):
        print(f"info :: Disabling bot...")
        self.close_logger()
        self.driver.close()
        self.driver.quit()

    def log_current_time(self):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H:%M")
        print(f"\ninfo :: Time: {dt_string}")

    def close_logger(self):
        self.handler.close()
        self.logger.removeHandler(self.handler)


def create_bot():
    try:
        KudosBot()
    except Exception as e:
        error_msg = f"error :: {e}"
        print(error_msg)


def send_mail_raport():
    mail_client = MailClient()
    mail_client.send_mail_raport()
    mail_client.close()


if __name__ == "__main__":
    schedule.every(60).minutes.do(create_bot)
    # schedule.every(4).hours.do(send_mail_raport)
    schedule.every().day.at("20:00").do(send_mail_raport)
    schedule.run_all()

    while True:
        schedule.run_pending()
        time.sleep(1)
