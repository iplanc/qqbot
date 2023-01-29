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
        message_to_send = qqbot.MessageSendRequest(content="暂无活动", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/禁言" in content:
        message_to_send = qqbot.MessageSendRequest(content="权限不足", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/帮助" in content:
        message_to_send = qqbot.MessageSendRequest(content="/查询 /信息 /活动 /禁言 /帮助", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/上岛" in content:
        message_to_send = qqbot.MessageSendRequest(content="预测值为：1200000", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/重启" in content:
        message_to_send = qqbot.MessageSendRequest(content="五秒后重启", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)
    elif "/状态" in content:
        message_to_send = qqbot.MessageSendRequest(content="状态良好", msg_id=message.id)
        await msg_api.post_message(message.channel_id, message_to_send)

async def channel_announce(t_token):
    api = qqbot.UserAPI(t_token, False)
    guilds = api.me_guilds()
    api = qqbot.ChannelAPI(t_token, False)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    for eachGuild in guilds:
        print(eachGuild.id, eachGuild.name)
        try:
            channels = api.get_channels(eachGuild.id)
            for eachChannel in channels:
                if (qqbot.ChannelAPI.get_channel(eachChannel).type == 0):
                    message_to_send = qqbot.MessageSendRequest(content="维护中，请等待")
                    await msg_api.post_message(eachGuild, message_to_send)
        except:
            pass

# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])

    # channel_announce(t_token)

    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler)
    qqbot.async_listen_events(t_token, False, qqbot_handler)
