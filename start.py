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

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))


def keywordsBlock(str):
    keywords = {
        "下注": "虾煮",
        "GTA": "给她爱",
        "赌场": "DC",
        "提示: 更多数据请使用小程序 “洛圣都 Express”查看": "",
    }
    for eachWord in keywords.keys():
        str = re.sub(eachWord, keywords.get(eachWord), str)
    return str.strip("\n")

class GTAVBot:
    msgapi = None
    message_reference = None
    member_api = None


    def __init__(self, t_token, message) -> None:
        self.msg_api = qqbot.AsyncMessageAPI(t_token, False)
        self.member_api = qqbot.GuildMemberAPI(t_token, False)
        self.message_reference = qqbot.MessageReference()
        self.message_reference.message_id = message.id

    async def getName(self, message):
        message_to_send = qqbot.MessageSendRequest(
            content = message.author.username,
            msg_id = message.id,
            message_reference = self.message_reference
        )
        await self.msg_api.post_message(message.channel_id, message_to_send)
        return message.author.username

    async def queryInfo(self, t_token, content, message):
        if content.split(" ")[2:] == []:
            username = re.sub(r".*id(:|：) ?", "", message.author.username.lower(), flags=re.M|re.I)
        else:
            username = content.split(" ")[2]
        self.message_reference = qqbot.MessageReference()
        self.message_reference.message_id = message.id
        response = requests.get(
            "https://hqshi.cn/api/recent",
            params = {"nickname": username, "expire": 7200, "type": "text"},
        )
        qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
        if response.json()["code"] == 400:
            message_to_send = qqbot.MessageSendRequest(
                content = response.json()["message"],
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
        elif response.json()["code"] == 202:
            message_to_send = qqbot.MessageSendRequest(
                content = response.json()["message"],
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
        elif response.json()["code"] == 303:
            message_to_send = qqbot.MessageSendRequest(
                content = await self.firstQuery(username, message),
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
        else:
            message_to_send = qqbot.MessageSendRequest(
                content = keywordsBlock(response.json()["body"]),
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)


    async def queryEvent(self, t_token, content, message):
        # 获取频道信息
        subChannelList = qqbot.ChannelAPI(t_token, False).get_channels(message.guild_id)
        for eachSubChannel in subChannelList:
            if "每周活动" in eachSubChannel.name:
                message_to_send = qqbot.MessageSendRequest(
                    content = "<#" + eachSubChannel.id + ">",
                    msg_id = message.id,
                    message_reference = self.message_reference
                )
                await self.msg_api.post_message(message.channel_id, message_to_send)


    async def queryData(self, t_token, content, message):
        if content.split(" ")[2:] == []:
            username = re.sub(r".*id(:|：) ?", "", message.author.username.lower(), flags=re.M|re.I)
        else:
            username = content.split(" ")[2]
        response = requests.get(
            "https://hqshi.cn/api/status", params = {"nickname": username, "limit": 1}
        )
        qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
        if response.json()["code"] == 400:
            message_to_send = qqbot.MessageSendRequest(
                content = response.json()["message"],
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
        else:
            if response.json().__contains__("body"):
                message_to_send = qqbot.MessageSendRequest(
                    content = keywordsBlock(
                        json.dumps(
                            response.json()["body"],
                            ensure_ascii = False,
                            indent = 4,
                            separators = (", ", ": "),
                        )
                    ),
                    msg_id = message.id,
                    message_reference = self.message_reference
                )
            else:
                await self.firstQuery(username, message)
                message_to_send = qqbot.MessageSendRequest(
                    content = "未查询到有效数据，请检查用户名后重新查询。",
                    msg_id = message.id,
                    message_reference = self.message_reference
                )
            await self.msg_api.post_message(message.channel_id, message_to_send)

    async def firstQuery(self, username, message):
        response = requests.get(
            "https://hqshi.cn/api/post", params = {"nickname": username}
        )
        qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
        message_to_send = qqbot.MessageSendRequest(
            content = response.json()["message"],
            msg_id = message.id,
            message_reference = self.message_reference
        )
        await self.msg_api.post_message(message.channel_id, message_to_send)
        for times in range(10, 0, -1):
            time.sleep(1)
            response1 = requests.get(
                "https://hqshi.cn/api/recent",
                params = {"nickname": username, "expire": 7200, "type": "text"},
            )
            if response1.json()["code"] == 200:
                return keywordsBlock(response1.json()["body"])
        return "请求超时，请稍后重试。"

    async def perico(self, t_token, content, message):
        total_value = 0
        main_loot = content.split(" ")[2]
        side_loot = content.split(" ")[3]
        difficult = content.split(" ")[4]

        cash = int(re.match("(\d)纸", side_loot).group(1)) if bool(re.match("\d纸", side_loot)) else 0
        weed = int(re.match("(\d)草", side_loot).group(1)) if bool(re.match("\d草", side_loot)) else 0
        coca = int(re.match("(\d)粉", side_loot).group(1)) if bool(re.match("\d粉", side_loot)) else 0
        gold = int(re.match("(\d)金", side_loot).group(1)) if bool(re.match("\d金", side_loot)) else 0
        draw = int(re.match("(\d)画", side_loot).group(1)) if bool(re.match("\d画", side_loot)) else 0

        # calc loot
        if (main_loot == "酒壶"):
            total_value = total_value + 900000
            total_value = total_value + cash * random.randint(104985, 110970)
            total_value = total_value + weed * random.randint(173970, 180000)
            total_value = total_value + coca * random.randint(263970, 270000)
            total_value = total_value + gold * random.randint(394080, 400080)
            total_value = total_value + draw * random.randint(210000, 240000)
        elif (main_loot == "项链"):
            total_value = total_value + 1000000
            total_value = total_value + cash * random.randint(96210, 101745)
            total_value = total_value + weed * random.randint(159480, 164970)
            total_value = total_value + coca * random.randint(241965, 247500)
            total_value = total_value + gold * random.randint(361224, 366720)
            total_value = total_value + draw * random.randint(192500, 220000)
        elif (main_loot == "债券"):
            total_value = total_value + 1100000
            total_value = total_value + cash * random.randint(91845, 97110)
            total_value = total_value + weed * random.randint(152235, 157500)
            total_value = total_value + coca * random.randint(230985, 236250)
            total_value = total_value + gold * random.randint(344808, 350064)
            total_value = total_value + draw * random.randint(183750, 210000)
        elif (main_loot == "粉钻"):
            total_value = total_value + 1300000
            total_value = total_value + cash * random.randint(87840, 92475)
            total_value = total_value + weed * random.randint(144990, 149985)
            total_value = total_value + coca * random.randint(219960, 225000)
            total_value = total_value + gold * random.randint(328392, 333384)
            total_value = total_value + draw * random.randint(175000, 200000)
        elif (main_loot == "豹子"):
            total_value = total_value + 1900000
            total_value = total_value + cash * random.randint(87840, 92475)
            total_value = total_value + weed * random.randint(144990, 149985)
            total_value = total_value + coca * random.randint(219960, 225000)
            total_value = total_value + gold * random.randint(328392, 333384)
            total_value = total_value + draw * random.randint(175000, 200000)
        elif (main_loot == "文件"):
            total_value = total_value + 1100000
            total_value = total_value + cash * random.randint(87840, 92475)
            total_value = total_value + weed * random.randint(144990, 149985)
            total_value = total_value + coca * random.randint(219960, 225000)
            total_value = total_value + gold * random.randint(328392, 333384)
            total_value = total_value + draw * random.randint(175000, 200000)
        if (difficult == "困难"):
            total_value = int(round(total_value * 1.1, -1))

        message_to_send = qqbot.MessageSendRequest(
            content = keywordsBlock("预计收入: " + str(total_value) + " " + str(round(total_value / 10000, 2)) + "w"),
            msg_id = message.id,
            message_reference = self.message_reference
        )
        await self.msg_api.post_message(message.channel_id, message_to_send)

    class Operate:
        msg_api = None
        mute_api = None
        guild_api = None
        user_api = None
        message_reference = None

        def __init__(self, t_token, message) -> None:
            self.msg_api = qqbot.AsyncMessageAPI(t_token, False)
            self.mute_api = qqbot.MuteAPI(t_token, False)
            self.guild_api = qqbot.GuildAPI(t_token, False)
            self.message_reference = qqbot.MessageReference()
            self.user_api = qqbot.UserAPI(t_token, False)
            self.message_reference.message_id = message.id


        async def muteUser(self, t_token, content, message):
            userid = content.split(" ")[2][3:-1]
            mutetime = content.split(" ")[3]
            setrole = ("博林布鲁克监狱服役人员" if content.split(" ")[4:] == [] else content.split(" ")[4])
            db = MySQLdb.connect(config["mysql"]["ip"], config["mysql"]["username"], config["mysql"]["password"], config["mysql"]["db"])
            cursor = db.cursor()
            print(re.sub(r" +", " ", r"""
                update mute set times=times+1 where guild_id="{guild_id}", user_id="{user_id}";

                select
                    if(times%3=0,
                        (select -1),
                        (
                            select times%3
                                from mute where guild_id="{guild_id}", user_id="{user_id}"
                        )
                    )
                    from mute where guild_id="{guild_id}", user_id="{user_id}";
            """.replace("\n", "").replace("{guild_id}", message.guild_id).replace("{user_id}", userid)))


        async def serverStatus(self, t_token, content, message):
            message_to_send = qqbot.MessageSendRequest(
                content = 'CPU: ' + re.search(r'\d+\.\d+$', os.popen("iostat -c").read(), re.M)[0] + '% 空闲',
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)


        async def guildInfo(self, t_token, content, message):
            for each in self.user_api.me_guilds():
                try:
                    guild = self.guild_api.get_guild(each.id)
                    message_to_send = qqbot.MessageSendRequest(
                        content = guild.id + '\n' + guild.name + '\n' + guild.owner_id + '\n' + str(guild.owner) + '\n' + str(guild.member_count) + '\n' + str(guild.max_members) + '\n' + guild.description,
                        image = each.icon,
                        msg_id = message.id,
                        message_reference = self.message_reference
                    )
                except:
                    # message_to_send = qqbot.MessageSendRequest(
                    #     content = "无权限频道id: " + each.id,
                    #     msg_id = message.id,
                    #     message_reference = self.message_reference
                    # )
                    print("无权限频道id: " + each.id)
                finally:
                    await self.msg_api.post_message(message.channel_id, message_to_send)

        async def reboot(self, t_token, content, message):
            message_to_send = qqbot.MessageSendRequest(
                content = "五秒后重启",
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
            print("manual reboot")
            os.system("python3 watchdog.py > watchdog.log")
            exit(1)


async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """
    gtavbot = GTAVBot(t_token, message)
    operate = GTAVBot.Operate(t_token, message)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    # 格式化输入
    left, right = re.search(r'/[\u4e00-\u9fa5][\u4e00-\u9fa5]', message.content, re.M).span()
    message.content = message.content[:right] + " " + message.content[right:]
    message.content = message.content[:left]  + " " + message.content[left:]
    message.content = re.sub(r" +", r" ", message.content.strip())
    # 运行命令
    if "/查询" in message.content:
        await gtavbot.queryInfo(t_token, message.content, message)

    elif "/活动" in message.content:
        await gtavbot.queryEvent(t_token, message.content, message)

    elif "/信息" in message.content:
        await gtavbot.queryData(t_token, message.content, message)

    elif "/禁言" in message.content:
        await operate.muteUser(t_token, message.content, message)

    elif "/状态" in message.content:
        await operate.serverStatus(t_token, message.content, message)

    elif "/频道" in message.content:
        await operate.guildInfo(t_token, message.content, message)

    elif "/上岛" in message.content:
        await gtavbot.perico(t_token, message.content, message)

    elif "/测试" in message.content:
        await gtavbot.getName(message)

    elif "/重启" in message.content:
        await operate.reboot(t_token, message.content, message)

# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(config["token"]["appid"], config["token"]["token"])

    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler)
