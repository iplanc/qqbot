# GTAOL 数据查询信息发布机器人
## 目录结构
- .gitignore
- readme.md
- start_fake.py
    - 专供审核用的假进程，只有输入输出功能，与真qq机器人进程共享appid
- start.py
    - qq机器人主文件
- start.sh
    - 封装好的一键启动脚本（没啥用）
- weekly.py
    - 每周活动发布机器人

## 配置流程
### config.yaml
```yaml
token:
  appid: "[appid]" # q.qq.com 获取到的appid
  token: "[token]" # q.qq.com 获取到的token
```

### weekly.py
```bash
Ubuntu
$ crontab -e
```
```
0 7 * * 5 python3 [path/to]/weekly.py
```
|0分|7时|每天|每月|周五|执行命令|
|:--|:--|:--|:--|:--|:--|
|0|7|*|*|5|python3 [path/to]/weekly.py|

## 二次开发
主要功能由此函数列出，其中的if结构体区别了各种命令
```python
async def _message_handler(event, message: qqbot.Message)
```
### 关键词屏蔽
通过字典定义的键值对进行替换敏感词，支持正则表达式
```python
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
```
### _message_handler()详解
该函数考研抽象为一下伪代码，收到@数据后对消息进行解析，去掉消息两侧的空格，正则表达式匹配消息中一个或多个空格将其替换成空格，查询命令是否在消息字符串中，执行操作
```python
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
        ...

    elif "/活动" in content:
        ...

    elif "/信息" in content:
        ...

    elif "/禁言" in content:
        ...
```
# 三分半掌握基础qq机器人开发
<video src="http://119.29.96.141:81/rickroll.mp4"></video>