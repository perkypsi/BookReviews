import csv
from datetime import datetime

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import os


class Vk_bot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.complete_application = False
        self.control_state_send = {
            "STATE_CONTACT": False,
            "STATE_GROUP": False,
            "STATE_TEXT": False
        }
        self.types_message = {
            "GREETING_MESSAGE": 'Здравствуйте, чтобы оставить нам жалобу или предложение напишите "Оставить заявку" '
                                'или воспользуйтесь соответствующей кнопкой',
            "CONTACT_DETAILS_MESSAGE": "Отлично! Для начала укажите ФИО.",
            "GROUP_DETAILS_MESSAGE": "Также укажите вашу группу.",
            "CONTENT_MESSAGE": "Теперь напишите полный текст сообщения, содержащий жалобу,предложение или вопрос.",
            "END_STATE": "Превосходно! Твоя заявка передана в Совет Обучающихся, после обработки мы обязательно "
                         "ответим тебе. До встречи! "
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

    def send_data(self):
        self.application['date'] = str(datetime.now())[:-7]
        self.application['id_vk'] = self.user_id

        application_info = [x for x in self.application.values()]
        with open('applications.csv', 'a', newline='') as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(application_info)
        self.control_state_send["STATE_SEND"] = False
        self.complete_application = True

    def write_msg(self, message, keyboard=None):
        post = {
            'user_id': self.user_id,
            'message': message,
            'random_id': 0
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
        elif self.control_state_send["STATE_CONTACT"]:
            self.get_contact(message=message)
        elif self.control_state_send["STATE_GROUP"]:
            self.get_group(message=message)
        elif self.control_state_send["STATE_TEXT"]:
            self.get_content(message=message)
            self.send_data()
        else:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Оставить заявку", VkKeyboardColor.NEGATIVE)
            self.write_msg(message=self.types_message["GREETING_MESSAGE"], keyboard=keyboard)


# API-ключ созданный ранее
token = "e0396ed76281c728a25841bf58f1049768b227e85cdaa7f51a073f79ddfcc1f8832e65acc800aaba20a0d"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Список подключенных ботов
bot_online = {}

print("Бот запущен")

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text.lower()

            # Имя пользователя
            user = str(event.user_id)

            if user in bot_online and bot_online[user] is not None:
                bot_online[user].act(request)
            else:
                bot_online[user] = Vk_bot(event.user_id)
                bot_online[user].act(request)
            for item in bot_online:
                if bot_online[item].complete_application:
                    bot_online[item] = None
