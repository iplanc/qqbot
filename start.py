from ast import keyword
import asyncio
import datetime
import json
import os.path
import threading
import time
import re
import requests
import sys

from typing import Dict, List

import aiohttp
import qqbot

from lxml import etree
from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import (
    MessageEmbed,
    MessageEmbedField,
    MessageEmbedThumbnail,
    CreateDirectMessageRequest,
    MessageArk,
    MessageArkKv,
    MessageArkObj,
    MessageArkObjKv,
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


async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    message.content = re.sub(r" +", r" ", message.content.strip())
    # 运行命令
    content = message.content
    if "/查询" in content:
        username = content.split(" ")[2]
        response = requests.get(
            "https://hqshi.cn/api/recent",
            params={"nickname": username, "expire": 7200, "type": "text"},
        )
        qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
        if response.json()["code"] == 400:
            message_to_send = qqbot.MessageSendRequest(
                content=response.json()["message"], msg_id=message.id
            )
            await msg_api.post_message(message.channel_id, message_to_send)
        elif response.json()["code"] == 202:
            message_to_send = qqbot.MessageSendRequest(
                content=response.json()["message"], msg_id=message.id
            )
            await msg_api.post_message(message.channel_id, message_to_send)
        elif response.json()["code"] == 303:
            response = requests.get(
                "https://hqshi.cn/api/post", params={"nickname": username}
            )
            qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
            message_to_send = qqbot.MessageSendRequest(
                content=response.json()["message"], msg_id=message.id
            )
            await msg_api.post_message(message.channel_id, message_to_send)
            time.sleep(10)
            message_to_send = qqbot.MessageSendRequest(
                content=keywordsBlock(
                    requests.get(
                        "https://hqshi.cn/api/recent",
                        params={"nickname": username, "expire": 7200, "type": "text"},
                    ).json()["body"]
                ),
                msg_id=message.id,
            )
            qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
            await msg_api.post_message(message.channel_id, message_to_send)
        else:
            message_to_send = qqbot.MessageSendRequest(
                content=keywordsBlock(response.json()["body"]), msg_id=message.id
            )
            await msg_api.post_message(message.channel_id, message_to_send)

    elif "/活动" in content:
        # 获取频道信息
        subChannelList = qqbot.ChannelAPI(t_token, False).get_channels(message.guild_id)
        for eachSubChannel in subChannelList:
            print("\t", eachSubChannel.id, eachSubChannel.name, eachSubChannel.type)
            if "每周活动" in eachSubChannel.name:
                print(eachSubChannel.name)
                message_to_send = qqbot.MessageSendRequest(
                    content="<#" + eachSubChannel.id + ">", msg_id=message.id
                )
                await msg_api.post_message(message.channel_id, message_to_send)

    elif "/信息" in content:
        username = content.split(" ")[2]
        response = requests.get(
            "https://hqshi.cn/api/status", params={"nickname": username, "limit": 1}
        )
        qqbot.logger.info(response.url + " status:" + str(response.json()["code"]))
        if response.json()["code"] == 400:
            message_to_send = qqbot.MessageSendRequest(
                content=response.json()["message"], msg_id=message.id
            )
            await msg_api.post_message(message.channel_id, message_to_send)
        else:
            if response.json().__contains__("body"):
                message_to_send = qqbot.MessageSendRequest(
                    content=keywordsBlock(
                        json.dumps(
                            response.json()["body"],
                            ensure_ascii=False,
                            indent=4,
                            separators=(", ", ": "),
                        )
                    ),
                    msg_id=message.id,
                )
            else:
                message_to_send = qqbot.MessageSendRequest(
                    content="未查询到有效数据，请检查用户名后重新查询。", msg_id=message.id
                )
            await msg_api.post_message(message.channel_id, message_to_send)

    elif "/禁言" in content:
        userid = content.split(" ")[2][3:-1]
        mutetime = content.split(" ")[3]
        setrole = (
            "博林布鲁克监狱服役人员" if content.split(" ")[4:] == [] else content.split(" ")[4]
        )
        qqbot.MuteAPI(t_token, False).mute_member(
            message.guild_id, userid, {"mute_seconds": mutetime}
        )
        message_to_send = qqbot.MessageSendRequest(
            content="已禁言" + userid, msg_id=message.id
        )
        await msg_api.post_message(message.channel_id, message_to_send)

        for eachRole in (
            qqbot.GuildRoleAPI(t_token, False).get_guild_roles(message.guild_id).roles
        ):
            if eachRole.name == setrole:
                qqbot.GuildRoleAPI(t_token, False).create_guild_role_member(
                    message.guild_id, eachRole.id, userid
                )
        message_to_send = qqbot.MessageSendRequest(
            content="已添加身份组" + userid, msg_id=message.id
        )
        await msg_api.post_message(message.channel_id, message_to_send)


# async def _create_ark_obj_list_recent(dict):
#     """
#     定义ark内容的处理
#     :param dict: 获取到的json对象
#     """
#     obj_list = [MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value="code：" + str(dict['code']) + "  payload：" + str(dict['payload']) + "  message：" + dict['message'])])]

#     for key in dict:
#         obj_list.append(MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value=re.sub("下注", "虾煮", dict[key]))]))

#     return obj_list


# async def _create_ark_obj_list_status(dict) -> List[MessageArkObj]:
#     """
#     定义ark内容的处理
#     :param dict: 获取到的json对象
#     """
#     obj_list = [MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value="code：" + str(dict['code']) + "  payload：" + str(dict['payload']) + "  message：" + dict['message'])])]

#     for key in dict['body']:
#         obj_list.append(MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value=key + ": " + str(dict['body'][key]))]))

#     return obj_list


# async def send_player_recent_ark_message(dict, channel_id, message_id):
#     """
#     被动回复-子频道推送模版消息
#     :param channel_id: 回复消息的子频道ID
#     :param message_id: 回复消息ID
#     :param dict: 玩家信息
#     """
#     # 构造消息发送请求数据对象
#     ark = MessageArk()
#     # 模版ID=23
#     ark.template_id = 23
#     ark.kv = [MessageArkKv(key="#DESC#", value="描述"),
#               MessageArkKv(key="#PROMPT#", value="提示消息"),
#               MessageArkKv(key="#LIST#", obj=await _create_ark_obj_list_recent(dict))]
#     # 通过api发送回复消息
#     send = qqbot.MessageSendRequest(content="", ark=ark, msg_id=message_id)
#     msg_api = qqbot.AsyncMessageAPI(t_token, False)
#     await msg_api.post_message(channel_id, send)


# async def send_player_status_ark_message(dict, channel_id, message_id):
#     """
#     被动回复-子频道推送模版消息
#     :param channel_id: 回复消息的子频道ID
#     :param message_id: 回复消息ID
#     :param dict: 玩家信息
#     """
#     # 构造消息发送请求数据对象
#     ark = MessageArk()
#     # 模版ID=23
#     ark.template_id = 23
#     ark.kv = [MessageArkKv(key="#DESC#", value="描述"),
#               MessageArkKv(key="#PROMPT#", value="提示消息"),
#               MessageArkKv(key="#LIST#", obj=await _create_ark_obj_list_status(dict))]
#     # 通过api发送回复消息
#     send = qqbot.MessageSendRequest(content="", ark=ark, msg_id=message_id)
#     msg_api = qqbot.AsyncMessageAPI(t_token, False)
#     await msg_api.post_message(channel_id, send)


# async def send_weekly_announce_by_time(token):
#     """
#     任务描述：每周推送一次活动信息
#     """
#     if ((datetime.datetime.now().weekday() + 1) == 5) and ((datetime.datetime.now().hour == 7)): # 如果是周五早上七点
#         # 获取活动数据
#         response = requests.get("https://socialclub.rockstargames.com/events/eventlisting?pageId=1&gameId=GTAV")
#         for each in response.json()['events']:
#             if 'linkToUrl' in each.keys():
#                 # print(each['linkToUrl'])
#                 headers = {"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"}
#                 response = requests.get("https://socialclub.rockstargames.com/" + each['linkToUrl'], headers=headers)
#                 event = etree.HTML(response.text)

#                 for eachGuild in qqbot.UserAPI(token, False).me_guilds():
#                     for eachChannel in qqbot.ChannelAPI(token, False).get_channels(eachGuild.id):
#                         if eachChannel.name == '每周活动':
#                             message = await qqbot.MessageAPI(token, False).post_message(eachChannel.id, {
#                                 "content": event.xpath(r'string(//*[@id="bespoke-panel"]/div[1])').replace(" ", "").replace("GTA", "给他爱"),
#                                 "msg_id": "0"
#                             })
#                             # announce = qqbot.AnnouncesAPI(token, False).create_announce(eachGuild.id, {
#                             #     "channel_id": eachChannel.id,
#                             #     "message_id": message.id
#                             # })

#                             break

#                 break
#     else:
#         pass
#     # 每小时执行一次
#     print("\t" + datetime.datetime.now())
#     t = threading.Timer(3600, await send_weekly_announce_by_time)
#     t.start()


# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])

    # send_weekly_announce_by_time(t_token)

    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler)
