import csv

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
import os


def write_msg(user_id, message, keyboard=None):
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': 0
    }
    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
    vk.method('messages.send', post)


def formation_application(app):
    with open('applications.csv', 'a', newline='') as out_csv:
        writer = csv.writer(out_csv)  # <_csv.writer object at 0x03B0AD80>
        writer.writerow(app)


# Сообщения бота

GREETING_MESSAGE = 'Здравствуйте, чтобы оставить нам жалобу или предложение напишите "Оставить заявку" ' \
                   'или воспользуйтесь соответствующей кнопкой'
CONTACT_DETAILS_MESSAGE = "Отлично! Для начала укажите ФИО."
GROUP_DETAILS_MESSAGE = "Также укажите вашу группу."
APPLICATION_MESSAGE = "Теперь напишите полный текст сообщения, содержащий жалобу,предложение или вопрос."
END_STATE = "Превосходно! Твоя заявка передана в Совет Обучающихся, после " \
            "обработки мы обязательно ответим тебе. До встречи!"

# API-ключ созданный ранее
token = "e0396ed76281c728a25841bf58f1049768b227e85cdaa7f51a073f79ddfcc1f8832e65acc800aaba20a0d"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

print("Бот запущен")

# Этапы отправки заявки

contact_date = False
group_date = False
text_message = False

# Сохранение заявки

NEW_APPLICATION = []
path = os.path.normpath(os.path.dirname(__file__))
# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text.lower()

            if request == "оставить заявку":
                write_msg(event.user_id, CONTACT_DETAILS_MESSAGE)
                contact_date = True
            elif contact_date:
                write_msg(event.user_id, GROUP_DETAILS_MESSAGE)
                NEW_APPLICATION.append(request)
                contact_date = False
                group_date = True
            elif group_date:
                write_msg(event.user_id, APPLICATION_MESSAGE)
                NEW_APPLICATION.append(request)
                group_date = False
                text_message = True
            elif text_message:
                write_msg(event.user_id, END_STATE)
                NEW_APPLICATION.append(request)
                text_message = False
                formation_application(NEW_APPLICATION)
                NEW_APPLICATION = []
            else:
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Оставить заявку", VkKeyboardColor.NEGATIVE)
                write_msg(event.user_id, GREETING_MESSAGE, keyboard=keyboard)
