# -*- coding: utf-8 -*-

import requests
import pandas as pd
import time
import logging
import os
import glob
import sqlite3

from configs import message_template, database_path

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage

def send_from_xlsx(viber_bot, file_path = ""):
    logging.basicConfig(filename = "viber_sender.log", level=logging.INFO)
    try:
        consolidation = []

        if not file_path:
            file_path = glob.glob(os.path.join(os.getcwd(), "*.xlsx"))[0]
        if not os.path.exists(file_path):
            print("Не найден файл по пути: {0}".format(file_path))
            logging.error("Не найден файл по пути: {0}".format(file_path))
            return
        data = pd.read_excel(file_path, header = None)
        rows = data.shape[0]

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        query = "SELECT id FROM phones WHERE phone=?" 

        for index in range(rows):
            try:
                info = list(map(str, data.iloc[index]))
                consolidation.append(info)
                if index + 1 < rows:
                    info_ahead = list(map(str, data.iloc[index + 1]))
                    if info_ahead[0] == "nan":
                        continue
            except:
                continue
            
            tel = consolidation[0][0].replace("+", "").replace(".0", "")
            text = message_template[0]
            for c in consolidation:
                text += message_template[1].format(*c) + "\n"

            try:
                cursor.execute(query, (tel))
                result = cursor.fetchone()[0]
                if not result: raise Exception("Сообщение на номер {0} не отправлено, потому что пользователя нет в базе".format(tel))
                user_id = result[0]

                viber_bot.send_messages(user_id, TextMessage(text=text))
                print("Сообщение на номер {0} успешно отправлено".format(tel))
                logging.info("Сообщение на номер {0} успешно отправлено".format(tel))
                
            except Exception as e:
                print(str(e))
                logging.error(str(e))
                

            consolidation.clear()
            time.sleep(1)
                
                
    except Exception as e:
        logging.error("Сбой программы:" + str(e))
        print(str(e))
        
        
    
