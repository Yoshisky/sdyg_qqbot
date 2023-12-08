# Python 3.10 +

import configparser
import re
import threading
import botpy
import asyncio
from botpy import logging, BotAPI
from botpy.message import Message, DirectMessage
from botpy.types.message import Reference, Embed, EmbedField, Thumbnail, Ark, ArkKv, MarkdownPayload, MessageMarkdownParams
from botpy.ext.command_util import Commands
from datetime import datetime
from botpy.errors import ServerError

from server_query_tool import Mcstatus


_log = logging.get_logger()
config = configparser.ConfigParser()
is_cron = False
try:
    config.read('config.cfg','UTF-8')
    is_cron = config.getboolean('cron', 'cronjob')
except Exception as e:
    _log.error(f"[init] {e}")

def find_dict_in_list(lst, key, value):
    for item in lst:
        if isinstance(item, dict) and key in item and item[key] == value:
            return item
    return None

def message_switch(msg = 'BOT不知道喔。。。'):
    # init query tool
    query = Mcstatus()

    content = ''
    match msg:
        case msg if msg.startswith('/help'):
            with open('help.txt', 'r', encoding='UTF-8') as f:
                content = f.read()
        case msg if msg.startswith('/list'):
            server1 = query.query_online_players(config.get('server', 'server1'))
            server2 = query.query_online_players(config.get('server', 'server2'))
            server3 = query.query_online_players(config.get('server', 'server3'))
            server4 = query.query_online_players(config.get('server', 'server4'))
            server5 = query.query_online_players(config.get('server', 'server5'))

            content = f'在线情况：\n1服：{server1}\n2服：{server2}\n3服：{server3}\n4服：{server4}\n5服：{server5}'

        case msg if msg.startswith('/1服'):
            content += '1服情况：'
            host = config.get('server', 'server1')
            content += query.query_detail(host)
        case msg if msg.startswith('/2服'):
            content += '2服情况'
            host = config.get('server', 'server2')
            content += query.query_detail(host)
        case msg if msg.startswith('/3服'):
            content += '3服情况'
            host = config.get('server', 'server3')
            content += query.query_detail(host)
        case msg if msg.startswith('/4服'):
            content += '4服情况'
            host = config.get('server', 'server4')
            content += query.query_detail(host)
        case msg if msg.startswith('/5服'):
            content += '5服情况'
            host = config.get('server', 'server5')
            content += query.query_detail(host)
        case msg if msg.startswith('/downloads'):
            content = query.query_saves(msg)
        case _:
            # echo
            content = msg

    return content

@Commands(name=("/list", "/1服", "/2服", "/3服", "/4服", "/5服", "/downloads", "/help"))
async def commands(api: BotAPI, message: Message, params=None):
    # _log.info(params)
    _log.info("[message] {} {}({})使用了指令".format(message.timestamp, message.author.username, message.author.id))
    msg = message.content.replace(re.search('<@![0-9]+>+', message.content).group(), '')
    msg = msg[1:]

    params = message_switch(msg)

    # 第一种用reply发送消息
    # await message.reply(content=params)
    # 第二种用api.post_message发送消息
    await api.post_message(channel_id=message.channel_id, content=params, msg_id=message.id)
    return True


class MyClient(botpy.Client):
    # hello world
    # startup logs
    async def on_ready(self):
        _log.info(f"[{self.__class__.__name__}]「{self.robot.name}」: Hello World!")
        _log.info(f"[{self.__class__.__name__}] 正在获取指定频道信息: {config.get('bot','guild_name')}")
        my_guild = await self.api.me_guilds()
        target_guild = find_dict_in_list(my_guild,'name',config.get('bot','guild_name'))
        guild_id = target_guild.get('id')
        _log.info(f'[{self.__class__.__name__}] 已获取指定频道信息: {await self.api.get_guild(guild_id)}')
        _log.info(f'[{self.__class__.__name__}] 正在获取指定子频道信息: {config.get("bot", "channel_name")}')
        channel_info = await self.api.get_channels(guild_id)
        target_channel = find_dict_in_list(channel_info,'name',config.get("bot", "channel_name"))
        _log.info(f'[{self.__class__.__name__}] 已获取指定子频道信息: {target_channel}')
        target_channel_id = target_channel.get('id')

        # wait 5 sec for data
        await asyncio.sleep(5)
        await self.cron_job_post_server_status(target_channel_id)

        # log all guild members
        # members = await self.api.get_guild_members(guild_id=guild_id, limit=100)
        # _log.info(f'[{self.__class__.__name__}] 当前频道成员（显示前100个）: {members}')

        # ark message can ONLY be seen on smartphone apps
        # payload: Ark = Ark(
        #     template_id=24,
        #     kv=[
        #         ArkKv(key='#METATITLE#', value='title'),
        #         ArkKv(key='#TITLE#', value='t2'),
        #         ArkKv(key='#PROMPT#', value='hello')
        #     ]
        # )
        # await self.api.post_message(
        #     channel_id=target_channel_id,
        #     ark=payload
        # )

    # 私信消息回复
    async def on_direct_message_create(self, message: DirectMessage):
        _log.info("[message] {} {}({})DM了机器人".format(message.timestamp, message.author.username,message.author.id))

        # send_message = 'BOT不知道喔。。。'
        # if "/test" in message.content:
        #     send_message = 'test'

        send_message = message_switch(message.content)

        await self.api.post_dms(
            guild_id=message.guild_id,
            content=send_message,
            msg_id=message.id,
        )

    # 指令回复+at消息回复
    async def on_at_message_create(self, message: Message):

        # 注册指令handler
        handlers = [
            commands,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return

        _log.info("[message] {} {}({})公开@了机器人".format(message.timestamp,message.author.username,message.author.id))
        # Remove at@ object
        msg = message.content.replace(re.search('<@![0-9]+>+',message.content).group(),'')
        msg = msg[1:]

        # plain回复
        ### await self.api.post_message(channel_id=message.channel_id, content="content")
        # await message.reply(content=f"{self.robot.name}发出了回音: {message.content}")
        # await asyncio.sleep(config.getint('bot','sleeptime'))

        # 引用回复
        # 构造消息发送请求数据对象
        message_reference = Reference(message_id=message.id)

        content = message_switch(msg)

        # 通过api发送回复消息
        await self.api.post_message(
            channel_id=message.channel_id,
            content=content,
            msg_id=message.id,
            message_reference=message_reference,
        )

    async def cron_job_post_server_status(self, channel_id='0'):
        interval = config.getint('cron', 'interval')
        # print(interval)
        if is_cron == True:
            _log.info(f'[{self.__class__.__name__}] 【定时任务】正在推送服务器信息，设定间隔: {interval}秒')
            # Get channel_id
            # target_guild_id = find_dict_in_list(await self.api.me_guilds(), 'name', config.get('bot', 'guild_name')).get('id')
            # target_channel_id = find_dict_in_list(await self.api.get_channels(target_guild_id), 'name', config.get("bot", "channel_name")).get('id')
            query = Mcstatus()
            target_channel_id = channel_id

            # embed = Embed(
            #     title=f"当前服务器信息（{datetime.now()}）",
            #     prompt="定时推送",
            #     fields=[
            #         EmbedField(name=f"1服: {query.query_online_players(config.get('server','server1'))}"),
            #         EmbedField(name=f"2服: {query.query_online_players(config.get('server','server2'))}"),
            #         EmbedField(name=f"3服: {query.query_online_players(config.get('server','server3'))}"),
            #         EmbedField(name=f"4服: {query.query_online_players(config.get('server','server4'))}"),
            #         EmbedField(name=f"5服: {query.query_online_players(config.get('server','server5'))}"),
            #     ],
            #     thumbnail=Thumbnail(url=config.get('cron','image_url')),
            # )
            # await self.api.post_message(
            #     channel_id=target_channel_id,
            #     # content="This message will resend in 30 sec",
            #     embed = embed
            # )

            content = (f"当前服务器信息 {datetime.now()}\n"
                       f"\n"
                       f"1服: {query.query_online_players(config.get('server','server1'))}\n"
                       f"2服: {query.query_online_players(config.get('server','server2'))}\n"
                       f"3服: {query.query_online_players(config.get('server','server3'))}\n"
                       f"4服: {query.query_online_players(config.get('server','server4'))}\n"
                       f"5服: {query.query_online_players(config.get('server','server5'))}\n")

            try:
                await self.api.post_message(
                    channel_id=target_channel_id,
                    content=content,
                    image=config.get('cron', 'image_url'),
                )
            except ServerError as e:
                _log.error(f'[{self.__class__.__name__}] 消息发送失败: {e}')

            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(interval)
            # pass
            return None
        t = threading.Timer(interval, await self.cron_job_post_server_status(target_channel_id))
        t.start()

        return None

intents = botpy.Intents(public_guild_messages=True,direct_message=True)
client = MyClient(intents=intents)
client.run(appid=config.get('bot','appid'), token=config.get('bot','token'))