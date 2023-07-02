#coding:utf-8
import json
import os
import qqbot
import requests

from lxml import etree

import Keywords

config = json.loads(open("./config.json", "r").read())

token = qqbot.Token(config["appid"], config["token"])

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
                                            "content": Keywords.Keywords.block(
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
