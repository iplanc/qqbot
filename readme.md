# GTAOL 数据查询信息发布机器人
## 命令
```
@机器人 /查询 ID
# 返回api获取到的数据
# 示例输出

>> 成功添加RockstarId至待处理列表, 当前还有1个待查询昵称

>> 昵称: planc26
>> 错误代号: 昵称不存在
>> 数据更新时间: 2022-05-18 18:31:24
>> 索引: AVVKNH
>> 查询状态: 201
```

```
@机器人 /信息 ID
# 返回api获取到的数据
# 示例输出

>> 成功添加RockstarId至待处理列表, 当前还有1个待查询昵称

>> {
>>     "昵称": "planc26", 
>>     "数据记录": {
>>         "索引": "AVVKNH", 
>>         "时间": "2022-05-18 18:31:24", 
>>         "状态": "昵称不存在", 
>>         "代号": 201
>>     }
>> }
```

```
@机器人 /活动
# 返回频道中第一个名字中带 "每周活动" 的聊天子频道
# 示例输出

>> #🌟速讯｜每周活动 
```

```
@机器人 /禁言 @成员 秒数 身分组
# 必须由频道主/管理员调用，禁言普通用户，必须是已存在的身分组（其实是犯懒了）
# 示例输出

>> 已禁言id
>> 已添加身份组id
```

### 隐藏命令
```
@机器人 /状态
# 返回服务器cpu状态
# 示例输出

>> Linux 5.4.0-77-generic (VM-8-6-ubuntu) 	05/18/2022 	_x86_64_	(1 CPU)

>> avg-cpu:  %user   %nice %system %iowait  %steal   %idle
>>            0.87    0.01    0.69    0.07    0.00   98.36
```

```
@机器人 /频道
# 返回机器人已加入的频道
```
## 部署
### 目录结构
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

### 配置流程
#### config.yaml
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
该函数可以抽象为以下伪代码，收到@数据后对消息进行解析，去掉消息两侧的空格，正则表达式匹配消息中一个或多个空格将其替换成空格，查询命令是否在消息字符串中，执行操作
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
    ...
```

### 警告禁言数据库交互
数据库采用MySQL
``` mermaid
sequenceDiagram
    participant qq频道
    participant 机器人
    participant 数据库

    qq频道 ->> 机器人 : "禁言用户id"
    机器人 ->> 数据库 : "查询是否存在数据，否则新建"
    数据库 -->> 机器人 : "存在"
    机器人 ->> 数据库 : "sql语句"
    数据库 -->> 机器人 : "返回被警告次数"
    机器人 -->> qq频道 : "禁言用户id"
```
```sql
update data_tbl set age=age+1 where id=2;

select
    if(age%3=0,
        (select -1),
        (
            select age%3
                from data_tbl where guild_id={guildid}, id={userid}
        )
    )
    from data_tbl where guild_id={guildid}, id={userid};
```
# 三分半掌握基础qq机器人开发
[视频链接](http://119.29.96.141:81/2k3jh8zx7f.mp4)
