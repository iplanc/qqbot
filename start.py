import aiohttp
import asyncio
import datetime
import json
import os
import qqbot
import re
import requests
import sqlite3
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
            username = re.sub(r"id(:|：) ?", "", message.author.username.lower(), flags=re.M|re.I)
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
                if times == 1:
                    message_to_send = qqbot.MessageSendRequest(
                        content = "请求超时，请稍后再试。", 
                        msg_id = message.id,
                        message_reference = self.message_reference
                    )
                    await self.msg_api.post_message(message.channel_id, message_to_send)
                    break
                if response1.json()["code"] == 200: 
                    message_to_send = qqbot.MessageSendRequest(
                        content = keywordsBlock(
                            response1.json()["body"]
                        ),
                        msg_id = message.id,
                        message_reference = self.message_reference
                    )
                    qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
                    await self.msg_api.post_message(message.channel_id, message_to_send)
                    break
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
            username = re.sub(r"id(:|：) ?", "", message.author.username.lower(), flags=re.M|re.I)
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
                message_to_send = qqbot.MessageSendRequest(
                    content = "未查询到有效数据，请检查用户名后重新查询。",
                    msg_id = message.id,
                    message_reference = self.essage_reference
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
            # self.mute_api.mute_member(
            #     guild_id = message.guild_id,
            #     user_id = userid,
            #     options = {"mute_seconds": mutetime}
            # )
            # message_to_send = qqbot.MessageSendRequest(
            #     content = "已禁言" + userid,
            #     msg_id = message.id,
            #     message_reference = self.message_reference
            # )
            # await self.msg_api.post_message(message.channel_id, message_to_send)

            # for eachRole in (self.guild_api.get_guild_roles(message.guild_id).roles):
            #     if eachRole.name ==  setrole:
            #         self.guild_api.create_guild_role_member(message.guild_id, eachRole.id, userid)
            # message_to_send = qqbot.MessageSendRequest(
            #     content = "已添加身份组" + userid,
            #     msg_id = message.id,
            #     message_reference = self.message_reference
            # )
            # await self.msg_api.post_message(message.channel_id, message_to_send)
        

        async def serverStatus(self, t_token, content, message):
            message_to_send = qqbot.MessageSendRequest(
                content = 'CPU: ' + re.search(r'\d+\.\d+$', os.popen("iostat -c").read(), re.M)[0] + '% 空闲', 
                msg_id = message.id,
                message_reference = self.message_reference
            )
            await self.msg_api.post_message(message.channel_id, message_to_send)
        

        async def guildInfo(self, t_token, content, message):
            for each in self.user_api.me_guilds():
                guild = self.guild_api.get_guild(each.id)
                message_to_send = qqbot.MessageSendRequest(
                    content = guild.id + '\n' + guild.name + '\n' + guild.owner_id + '\n' + str(guild.owner) + '\n' + str(guild.member_count) + '\n' + str(guild.max_members) + '\n' + guild.description,
                    image = each.icon,
                    msg_id = message.id,
                    message_reference = self.message_reference
                )
                await self.msg_api.post_message(message.channel_id, message_to_send)

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
    
    elif "/测试" in message.content:
        await gtavbot.getName(message)

# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])

    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler)
