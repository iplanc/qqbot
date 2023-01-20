#coding:utf-8

import aiohttp
import asyncio
import datetime
import json
import MySQLdb
import os
import qqbot
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

test_config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))

token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])


def keywordsBlock(str):
    keywords = {
        "下注": "虾煮",
        "GTA": "给她爱",
        "赌场": "DC",
        "提示: 更多数据请使用小程序 “洛圣都 Express”查看": "",
        " ": "",
    }
    for eachWord in keywords.keys():
        str = str.replace(eachWord, keywords.get(eachWord))
    return str.strip("\n")


response = requests.get(
    "https://socialclub.rockstargames.com/events/eventlisting?pageId=1&gameId=GTAV"
)
for each in response.json()["events"]:
    if "linkToUrl" in each.keys():
        # print(each['linkToUrl'])
        headers = {"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"}
        response = requests.get(
            "https://socialclub.rockstargames.com/" + each["linkToUrl"], headers=headers
        )
        event = etree.HTML(response.text)
        print(each)
        print(response.url)

        for eachGuild in qqbot.UserAPI(token, False).me_guilds():
            print(eachGuild.name)
            permissions = qqbot.APIPermissionAPI(token, False).get_permissions(eachGuild.id)
            for eachPermission in permissions:
                if eachPermission.path == "/guilds/{guild_id}/channels":
                    if eachPermission.auth_status == 1:
                        for eachChannel in qqbot.ChannelAPI(token, False).get_channels(eachGuild.id):
                            if "每周活动" in eachChannel.name:
                                print("    " + eachChannel.name)
                                try:
                                    message = qqbot.MessageAPI(token, False).post_message(
                                        eachChannel.id,
                                        {
                                            "content": keywordsBlock(
                                                event.xpath(r'string(//*[@id="bespoke-panel"]/div[1])')
                                            ),
                                            "msg_id": "0",
                                        },
                                    )
                                except:
                                    print("出错")
                                break
                    else:
                        break
        break
