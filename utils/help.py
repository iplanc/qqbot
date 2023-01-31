import qqbot
import textwrap

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

class HelpInfo():
    def info(self):
        return textwrap.dedent("""
        输入"/"可快速打开机器人命令列表
        可将昵称改为"你的昵称 | id:你的游戏id"，当使用查询和信息查询本人信息时可以省略游戏id
            例："嘉心糖 | id:PlanC14"✔ "小哑巴 | ID：PlanC14"✔ "PlanC14"❌
        可新建一个名称中带有"每周活动"的子频道，机器人会在每周五上午九点自动获取r星官网新闻并转发
            例："R星每周活动"✔ "速讯|每周活动"✔ "每周|活动"❌
        ---
        @机器人 /帮助 = 输出此消息
        @机器人 /查询 游戏id = 查询两小时内最新数据，若未找到，则下载最新数据
        @机器人 /信息 游戏id = 查询账户信息
        @机器人 /活动 = 返回第一个名字中带有"每周活动"的聊天子频道
        @机器人 /禁言 = 暂不可用
        @机器人 /上岛 主要战利品 次要战利品 难度 = 预测上岛收入
            例：@机器人 /上岛 酒壶 1金1草1面1画1纸 困难
            例：@机器人 /上岛 酒壶 无 普通
            主要战利品为：酒壶 项链 债券 豹子 粉钻 文件
            次要战利品为：金 草 面 画 纸
        @机器人 /重启 = 快速重启机器人，仅管理员可用
        @机器人 /状态 = 查看服务器状态，仅管理员可用
        """)[1:]

    async def print(self, t_token, content, message):
        message_to_send = qqbot.MessageSendRequest(
            content = self.info(),
            msg_id = message.id,
            message_reference = qqbot.MessageReference(message_id = message.id)
        )
        await qqbot.AsyncMessageAPI(t_token, False).post_message(message.channel_id, message_to_send)

