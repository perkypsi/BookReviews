import random

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from commander.commander import Commander


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


GREETING_MESSAGE = 'Привет, чтобы оставить нам жалобу или предложение напиши "Оставить заявку" ' \
                   'или воспользуйся соответствующейся кнопкой'

CONTACT_DETAILS_MESSAGE = "Отлично! Для начала укажи ФИО и номер группы."

APPLICATION_MESSAGE = "Теперь напиши полный текст сообщения, содержащий жалобу или предложение."

END_STATE = "Превосходно! Твоя заявка передана в Совет Обучающихся, после " \
            "обработки мы обязательно ответим тебе. До встречи!"

# API-ключ созданный ранее
token = "e0396ed76281c728a25841bf58f1049768b227e85cdaa7f51a073f79ddfcc1f8832e65acc800aaba20a0d"

# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Commander
commander = Commander()

# keyboard = VkKeyboard(one_time=True)
# keyboard.add_button('Привет', color=VkKeyboardColor.PRIMARY)
# keyboard.add_button('Клавиатура', color=VkKeyboardColor.POSITIVE)
# keyboard.add_line()
# keyboard.add_location_button()
# keyboard.add_line()
# keyboard.add_vkpay_button(hash="action=transfer-to-group&group_id=еще_раз_ID_группы")

print("Бот запущен")

# Этапы отправки заявки

contact_date = False
text_message = False

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня( то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text.lower()

            keyboard = VkKeyboard()
            keyboard.add_button("Оставить заявку", VkKeyboardColor.PRIMARY)

            if request == "оставить заявку":
                write_msg(event.user_id, CONTACT_DETAILS_MESSAGE)
                contact_date = True
            elif contact_date:
                write_msg(event.user_id, APPLICATION_MESSAGE)
                contact_date = False
                text_message = True
            elif text_message:
                write_msg(event.user_id, END_STATE)
                text_message = False
            else:
                write_msg(event.user_id, GREETING_MESSAGE, keyboard=keyboard)


