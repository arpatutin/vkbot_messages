import json
import time

import requests
import vk_api

session = vk_api.VkApi(token="13fe255b767fb7a82b1f742ea3111ea9abef8460f03f143afe2d93b807f075d1d932ee72540bd723c40e5")

from vk_api.longpoll import VkLongPoll, VkEventType
longpool = VkLongPoll(session, 196273828)
api = session.get_api()

statuses = {}


def get_id_by_link(link):
    post = link.split("/")[-1]
    user = json.loads(requests.get("https://api.vk.com/method/users.get?user_ids=%s&access_token=13fe255b767fb7a82b1f742ea3111ea9abef8460f03f143afe2d93b807f075d1d932ee72540bd723c40e5&v=5.110" % post).text)
    return user["response"][0]["id"]


while 1:
    for event in longpool.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() == "начать":
                statuses[event.user_id] = {"status": "started", "anonymous": None,
                                           "user": None, "text": None}
                api.messages.send(
                    user_id=event.user_id,
                    message="Привет! Введи команду:".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_main.json").read()
                )
            elif event.text.lower() == "информация для доната":
                api.messages.send(
                    user_id=event.user_id,
                    message="Донатить на Qiwi +79889593007".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_main.json").read()
                )
            elif event.text.lower() == "что умеет этот бот":
                api.messages.send(
                    user_id=event.user_id,
                    message="""Этот бот умеет отправлять ваши сообщения пользователям
                    от имени сообщества. Отправляются сообщения анонимно или нет - выбираете вы.
                    Искренне ваш,
                           создатель бота.""".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_main.json").read()
                )
            elif event.text.lower() == "отправить сообщение" and statuses[event.user_id]["status"] == "started":
                statuses[event.user_id]["status"] = "0"
                api.messages.send(
                    user_id=event.user_id,
                    message="Отправить анонимно?".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_anonimno.json").read()
                )
            elif event.text.lower() == "да" and statuses[event.user_id]["status"] == "0":
                statuses[event.user_id]["anonymous"] = True
                statuses[event.user_id]["user"] = "wait"
                api.messages.send(
                    user_id=event.user_id,
                    message="Введите ссылку на профиль пользователя:".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_back.json").read()
                )
            elif event.text.lower() == "нет" and statuses[event.user_id]["status"] == "0":
                statuses[event.user_id]["anonymous"] = True
                statuses[event.user_id]["user"] = "wait"
                api.messages.send(
                    user_id=event.user_id,
                    message="Введите ссылку на профиль пользователя (без слеша в конце):".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_back.json").read()
                )
            elif statuses[event.user_id]["user"] == "wait":
                statuses[event.user_id]["user"] = event.text
                statuses[event.user_id]["text"] = "wait"
                api.messages.send(
                    user_id=event.user_id,
                    message="Введите сообщение:".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_back.json").read()
                )
            elif event.text.lower() == "назад" and (statuses[event.user_id]["user"] == "wait" or statuses[event.user_id]["text"] == "wait"):
                api.messages.send(
                    user_id=event.user_id,
                    message="Привет! Введи команду:".encode("utf-8").strip(),
                    random_id=time.time(),
                    keyboard=open("keyboard_main.json").read()
                )
            elif statuses[event.user_id]["text"] == "wait":
                statuses[event.user_id]["text"] = event.text
                try:
                    if statuses[event.user_id]["anonymous"]:
                        user_id = "Аноним"
                    else:
                        user_id = f"{api.method('users.get', event.user_id)['first_name']} {api.method('users.get', event.user_id)['last_name']}"
                    api.messages.send(
                        user_id=get_id_by_link(statuses[event.user_id]["user"]),
                        message=f"{user_id} отправил вам сообщение:\n{statuses[event.user_id]['text']}\nОтправьте так же! Пишите сообществу!".encode(
                            "utf-8").strip(),
                        random_id=time.time(),
                    )
                    api.messages.send(
                        user_id=event.user_id,
                        message="Сообщение отправлено.".encode(
                            "utf-8").strip(),
                        random_id=time.time(),
                    )
                except:
                    api.messages.send(
                        user_id=event.user_id,
                        message="Пользователь запретил себе писать.".encode(
                            "utf-8").strip(),
                        random_id=time.time(),
                        keyboard=open("keyboard_back.json").read()
                    )
                finally:
                    statuses[event.user_id] = {"status": "start"}
                    api.messages.send(
                        user_id=event.user_id,
                        message="Привет! Введи команду:".encode("utf-8").strip(),
                        random_id=time.time(),
                        keyboard=open("keyboard_main.json").read()
                    )
