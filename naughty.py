import math
import aiohttp
import asyncio
import datetime
import json
import MySQLdb
import os
import qqbot
import random
import re
import requests
import sys
import threading
import time

from ast import keyword
from lxml import etree
from typing import Dict, List

from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import (
    CreateDirectMessageRequest,
    MessageArk,
    MessageArkKv,
    MessageArkObj,
    MessageArkObjKv,
    MessageEmbed,
    MessageEmbedField,
    MessageEmbedThumbnail,
)

chatroom = [".*闲聊.*", ".*聊天.*", ".*交流.*"]

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))
db = MySQLdb.connect(config["mysql"]["ip"], config["mysql"]["username"], config["mysql"]["password"], config["mysql"]["db"])
token = qqbot.Token(config["token"]["appid"], config["token"]["token"])

def bullshit():
    with open("data.json", mode='r', encoding="utf-8") as file:
        data = json.loads(file.read())
        名人名言 = data["famous"] # a 代表前面垫话，b代表后面垫话
        前面垫话 = data["before"] # 在名人名言前面弄点废话
        后面垫话 = data['after']  # 在名人名言后面弄点废话
        废话 = data['bosh'] # 代表文章主要废话来源
        xx = "移除机器人"

        下一句废话 = 洗牌遍历(废话)
        下一句名人名言 = 洗牌遍历(名人名言)

        tmp = str()
        while ( len(tmp) < 200 ) :
            分支 = random.randint(0,100)
            if 分支 < 5:
                x = "\r\n"
                x += "    "
                tmp += x
            elif 分支 < 20 :
                x = next(下一句名人名言)
                x = x.replace(  "a",random.choice(前面垫话) )
                x = x.replace(  "b",random.choice(后面垫话) )
                tmp += x
            else:
                tmp += next(下一句废话)
        tmp = tmp.replace("x",xx)
        return tmp

def 洗牌遍历(列表):
    global 重复度
    池 = list(列表) * 2
    while True:
        random.shuffle(池)
        for 元素 in 池:
            yield 元素

if __name__ == "__main__":
    results = config["unauthorized_guild"]
    # cursor = db.cursor()
    # cursor.execute("select * from unauthorized_guild")
    # results = cursor.fetchall()
    for row in results:
        # print(row[0])
        print(row)
        channels = qqbot.ChannelAPI(token, False).get_channels(row)
        for channel in channels:
            if channel.type == 0:
                print(channel.name)
                for each in chatroom:
                    if re.match(each, channel.name):
                        print("this")
                        for i in range(0, 20):
                            qqbot.MessageAPI(token, False).post_message(channel.id, {
                                "content": bullshit(),
                                "msg_id": "0"
                            })

    db.close()