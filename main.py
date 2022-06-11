# -*- coding: utf-8 -*-

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages import KeyboardMessage
import logging
import sqlite3

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

import configs, viber_sender
app = Flask(__name__)
viber = Api(BotConfiguration(
    name=configs.bot_name,
    avatar=configs.bot_avatar,
    auth_token=configs.BOT_TOKEN
))
viber.set_webhook(configs.webhook_link)

logging.basicConfig(filename="server.log", level=logging.INFO)
debug = True
keyboard = {
	"keyboard": {
		"DefaultHeight": True,
		"BgColor": "#FFFFFF",
		"Buttons": [{
			"BgColor": "#2bb52b",
			"ActionType": "share-phone",
                        "ActionBody": "phone",
			"Text": "Поделиться номером телефона"
		}]
	}
}
def db_find(user_id):
    connection = sqlite3.connect(configs.database_path)
    curr = connection.cursor()
    curr.execute("SELECT phone FROM phones WHERE id=?", [(user_id)])
    result = curr.fetchone()[0]
    connection.close()
    return result != None

@app.route('/', methods=['POST'])
def incoming():  
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)
    
    if debug:
        logging.debug("received request. post data: {0}".format(request.get_data()))

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        user_id = str(viber_request.get_user().get_id())
        if user_id == configs.admin_id:
            send_from_xlsx(viber)
        message = viber_request.message
##        tel = ""
        logging.info(str(message))
        print(str(message))
##        if not db_find(user_id):  
##            curr.execute("INSERT INTO phones(id, phone) VALUES(?, ?)", [(user_id, tel)])
##            curr.commit()
##            logging.info(f"Пользователь {user_id} с номером {tel} успешно добавлен в базу")

    if isinstance(viber_request, ViberConversationStartedRequest):
        user_id = viber_request.get_user().get_id()
        viber.send_messages(user_id, [
			TextMessage(text="Добро пожаловать! Не забудьте поделиться своим номером телефона, нажав на кнопку 'Поделиться номером телефона' внизу.\n \
                                    Без этого действия я не смогу присылать вам уведомления"),
                        KeyboardMessage(keyboard=keyboard, min_api_version=3)
		])
        
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user().get_id(), [
            TextMessage(text="Вы были добавлены в !")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logging.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

if __name__ == "__main__":
    app.run(host=configs.host, port=8443, debug=True)
