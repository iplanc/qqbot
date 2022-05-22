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

test_config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config_fake.yaml"))

async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    # 运行命令
    content = message.content
    if "/查询" in content:
        message_to_send = qqbot.MessageSendRequest(content="年龄：18", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/信息" in content:
        message_to_send = qqbot.MessageSendRequest(content="性别：男", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/活动" in content:
        # 获取已加入的频道信息
        channelList = qqbot.UserAPI(t_token, False).me_guilds()
        # print(message.guild_id, message.channel_id)
        subChannelList = qqbot.ChannelAPI(t_token, False).get_channels(message.guild_id)
        for eachSubChannel in subChannelList:
            # print("\t", eachSubChannel.id, eachSubChannel.name, eachSubChannel.type)
            if eachSubChannel.type == 10007:
                message_to_send = qqbot.MessageSendRequest(content="<#"+ eachSubChannel.id + ">", msg_id=message.id)
                await msg_api.post_message(message.channel_id, message_to_send)
                break
    elif "/禁言" in content:
        userid = content.split(" ")[2][3:-1]
        mutetime = content.split(" ")[3]
        print("\ttime:", datetime.datetime.now())
        print("\tid:", qqbot.GuildMemberAPI(t_token, False).get_guild_member(message.guild_id, userid).user.id)
        print("\tusername:", qqbot.GuildMemberAPI(t_token, False).get_guild_member(message.guild_id, userid).user.username)
        print("\tavatar:", qqbot.GuildMemberAPI(t_token, False).get_guild_member(message.guild_id, userid).user.avatar)
        print("\tisbot:", qqbot.GuildMemberAPI(t_token, False).get_guild_member(message.guild_id, userid).user.bot)
        message_to_send = qqbot.MessageSendRequest(content="已禁言" + userid + " " + mutetime + "秒", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)

def channel_info():
    api = qqbot.UserAPI(t_token, False)
    guilds = api.me_guilds()
    api = qqbot.ChannelAPI(t_token, False)
    for eachGuild in guilds:
        print(eachGuild.id, eachGuild.name)
        channels = api.get_channels(eachGuild.id)
        for eachChannel in channels:
            print("\t", eachChannel.id, eachChannel.name, eachChannel.type)

# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])

    channel_info()
    
    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler)
    qqbot.async_listen_events(t_token, False, qqbot_handler)
    