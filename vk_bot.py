# -*- coding: utf-8 -*-

import csv
import random
from datetime import datetime
import logging
from settings import TOKEN

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

"""Use Python 3.8"""

class Vk_bot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.complete_application = False
        self.control_state_send = {
            "STATE_CONTACT": False,
            "STATE_GROUP": False,
            "STATE_TEXT": False,
            "STATE_FEEDBACK": False
        }
        self.types_message = {
            "GREETING_MESSAGE": 'Здравствуйте, чтобы оставить нам жалобу или предложение напишите "Оставить заявку" '
                                'или воспользуйтесь соответствующей кнопкой',
            "CONTACT_DETAILS_MESSAGE": "Отлично! Для начала укажите ФИО.",
            "GROUP_DETAILS_MESSAGE": "Также укажите вашу группу.",
            "CONTENT_MESSAGE": "Теперь напишите полный текст сообщения, содержащий жалобу, предложение или вопрос.",
            "END_STATE": "Перед тем, как заявка будет отправлена, поставьте, пожалуйста, оценку работы и удобства "
                         "бота по 10-ти бальной шкале.",
            "FEEDBACK_STATE": "Превосходно! Твоя заявка передана в Совет Обучающихся, после обработки мы обязательно "
                              "ответим тебе! Спасибо за ваш отзыв! До встречи! "
        }
        self.application = {
            'date': '',
            'id_vk': '',
            'contact': '',
            'group': '',
            'content': '',
            'feedback': ''
        }

    def get_contact(self, message):
        self.write_msg(message=self.types_message["GROUP_DETAILS_MESSAGE"])
        self.application['contact'] = message
        self.control_state_send["STATE_CONTACT"] = False
        self.control_state_send["STATE_GROUP"] = True

    def get_group(self, message):
        self.write_msg(message=self.types_message["CONTENT_MESSAGE"])
        self.application['group'] = message
        self.control_state_send["STATE_GROUP"] = False
        self.control_state_send["STATE_TEXT"] = True

    def get_content(self, message):
        self.write_msg(message=self.types_message["END_STATE"])
        self.application['content'] = message
        self.control_state_send["STATE_TEXT"] = False
        self.control_state_send["STATE_FEEDBACK"] = True

    def get_feedback(self, message):
        self.write_msg(message=self.types_message["FEEDBACK_STATE"])
        try:
            feedback = int(message)
        except ValueError:
            self.application['feedback'] = message
        else:
            self.application['feedback'] = feedback
        self.control_state_send["STATE_FEEDBACK"] = False

    def send_data(self):
        self.application['date'] = str(datetime.now())[:-7]
        self.application['id_vk'] = self.user_id

        application_info = [x for x in self.application.values()]
        with open('applications.csv', 'a', newline='', encoding='utf8') as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(application_info)
        self.control_state_send["STATE_SEND"] = False
        log.debug("Данные сформированы и записаны в файл")
        self.complete_application = True

    def write_msg(self, message, keyboard=None):
        post = {
            'user_id': self.user_id,
            'message': message,
            'random_id': random.randint(0, 10000)
        }
        if keyboard is not None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post = post
        vk.method('messages.send', post)

    def act(self, message):

        if message == "оставить заявку":
            self.write_msg(message=self.types_message["CONTACT_DETAILS_MESSAGE"])
            self.control_state_send["STATE_CONTACT"] = True
            log.info(f"{self.user_id} оставил заявку")
        elif self.control_state_send["STATE_CONTACT"]:
            self.get_contact(message=message)
            log.info(f"{self.user_id} оставил контакты")
        elif self.control_state_send["STATE_GROUP"]:
            self.get_group(message=message)
            log.info(f"{self.user_id} оставил данные группы")
        elif self.control_state_send["STATE_TEXT"]:
            self.get_content(message=message)
            log.info(f"{self.user_id} оставил содержание заявки")
        elif self.control_state_send["STATE_FEEDBACK"]:
            self.get_feedback(message=message)
            log.info(f"{self.user_id} оставил оценку")
            self.send_data()
        else:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Оставить заявку", VkKeyboardColor.NEGATIVE)
            self.write_msg(message=self.types_message["GREETING_MESSAGE"], keyboard=keyboard)


def log_configure(log_program):
    file_handler = logging.FileHandler("bot.log", mode='w', encoding='utf8')
    file_handler.setFormatter(logging.Formatter("%(asctime)ss| %(levelname)s | %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    log_program.addHandler(file_handler)


# Запуск средства логирования
log = logging.getLogger("log_chat_bot")
log_configure(log)
log.setLevel(logging.DEBUG)

# API-ключ созданный ранее
token = TOKEN

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Список подключенных ботов
bot_online = {}

log.debug("Бот активен")

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            log.info(f"Пришло сообщение от {event.user_id} с содержанием: {event.text}")
            request = event.text.lower()

            # Имя пользователя
            user = str(event.user_id)

            if user in bot_online and bot_online[user] is not None:
                log.debug(f"Объект {user} есть в списке")
                bot_online[user].act(request)
                if len(bot_online) != 0:
                    for item in bot_online:
                        if bot_online[item].complete_application:
                            log.debug(f"Объект {bot_online[item]} удален из списка")
                            bot_online[item] = None
                            bot_online.pop(item)
                        if len(bot_online) == 0:
                            break

            else:
                log.debug(f"Объекта {user} нет в списке")
                bot_online[user] = Vk_bot(event.user_id)
                bot_online[user].act(request)
                log.debug(f"Словарь действующих ботов: {bot_online}")
