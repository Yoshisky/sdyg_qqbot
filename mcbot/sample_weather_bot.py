import asyncio
import json
import os.path
import threading
from typing import Dict, List

import aiohttp
import qqbot

from qqbot.core.util.yaml_util import YamlUtil
from qqbot.model.message import MessageEmbed, MessageEmbedField, MessageEmbedThumbnail, CreateDirectMessageRequest, \
    MessageArk, MessageArkKv, MessageArkObj, MessageArkObjKv

test_config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))

# async def _message_handler(event, message: qqbot.Message):
#     """
#     定义事件回调的处理
#     :param event: 事件类型
#     :param message: 事件对象（如监听消息是Message对象）
#     """
#     msg_api = qqbot.AsyncMessageAPI(t_token, False)
#     # 打印返回信息
#     qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理
    :param event: 事件类型
    :param message: 事件对象（如监听消息是Message对象）
    """
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    # 获取天气数据并发送消息告知用户
    weather_dict = await get_weather("深圳")
    weather_desc = weather_dict['result']['citynm'] + " " \
        + weather_dict['result']['weather'] + " " \
        + weather_dict['result']['days'] + " " \
        + weather_dict['result']['week']
    message_to_send = qqbot.MessageSendRequest(msg_id=message.id, content=weather_desc, image=weather_dict['result']['weather_icon'])
    await msg_api.post_message(message.channel_id, message_to_send)
    
 # 根据指令触发不同的推送消息
    content = message.content
    if "/天气" in content:
         # 通过空格区分城市参数
        split = content.split("/天气 ")
        weather = await get_weather(split[1])
        await send_weather_ark_message(weather, message.channel_id, message.id)


    elif "/私信天气" in content:
        # 通过空格区分城市参数
        split = content.split("/私信天气 ")
        weather = await get_weather(split[1])
        await send_weather_embed_direct_message(weather, message.guild_id, message.author.id)

        

    # weather
async def get_weather(city_name: str) -> Dict:
    """
    获取天气信息
    :return: 返回天气数据的json对象
    """
    weather_api_url = "http://api.k780.com/?app=weather.today&cityNm=" + city_name + "&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4&format=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=weather_api_url,
                timeout=5,
        ) as resp:
            content = await resp.text()
            content_json_obj = json.loads(content)
            return content_json_obj



    # 发送消息告知用户
    message_to_send = qqbot.MessageSendRequest(content="你好", msg_id=message.id)
    await msg_api.post_message(message.channel_id, message_to_send)


# async的异步接口的使用示例
if __name__ == "__main__":
    t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])
    # @机器人后推送被动消息
    qqbot_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot.async_listen_events(t_token, False, qqbot_handler)
     # 定时推送主动消息
    send_weather_message_by_time()



async def send_weather_message_by_time():
    """
    任务描述：每天推送一次普通天气消息（演示方便改为100s定时运行）
    """
    # 获取天气数据
    weather_dict = await get_weather("深圳")
    # 获取频道列表都取首个频道的首个子频道推送
    user_api = qqbot.AsyncUserAPI(t_token, False)
    guilds = await user_api.me_guilds()
    guilds_id = guilds[0].id
    channel_api = qqbot.AsyncChannelAPI(t_token, False)
    channels = await channel_api.get_channels(guilds_id)
    channels_id = channels[0].id
    qqbot.logger.info("channelid %s" % channel_id)
    # 推送消息
    weather = "当前天气是：" + weather_dict['result']['weather']
    send = qqbot.MessageSendRequest(content=weather)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    await msg_api.post_message(channels_id, send)
    # 如果需要每天都执行，加上下面两句
    t = threading.Timer(100, await send_weather_message_by_time)
    t.start()


async def _create_ark_obj_list(weather_dict) -> List[MessageArkObj]:
    obj_list = [MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value=weather_dict['result']['citynm'] + " " + weather_dict['result']['weather'] +  " " + weather_dict['result']['days'] + " " + weather_dict['result']['week'])]),
                MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value="当日温度区间：" + weather_dict['result']['temperature'])]),
                MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value="当前温度：" + weather_dict['result']['temperature_curr'])]),
                MessageArkObj(obj_kv=[MessageArkObjKv(key="desc", value="当前湿度：" + weather_dict['result']['humidity'])])]
    return obj_list

async def send_weather_ark_message(weather_dict, channel_id, message_id):
    """
    被动回复-子频道推送模版消息
    :param channel_id: 回复消息的子频道ID
    :param message_id: 回复消息ID
    :param weather_dict:天气消息
    """
    # 构造消息发送请求数据对象
    ark = MessageArk()
    # 模版ID=23
    ark.template_id = 23
    ark.kv = [MessageArkKv(key="#DESC#", value="描述"),
              MessageArkKv(key="#PROMPT#", value="提示消息"),
              MessageArkKv(key="#LIST#", obj=await _create_ark_obj_list(weather_dict))]
    # 通过api发送回复消息
    send = qqbot.MessageSendRequest(content="", ark=ark, msg_id=message_id)
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    await msg_api.post_message(channel_id, send)



async def send_weather_embed_direct_message(weather_dict, guild_id, user_id):
    """
    被动回复-私信推送天气内嵌消息
    :param user_id: 用户ID
    :param weather_dict: 天气数据字典
    :param guild_id: 发送私信需要的源频道ID
    """
    # 构造消息发送请求数据对象
    embed = MessageEmbed()
    embed.title = weather_dict['result']['citynm'] + " " + weather_dict['result']['weather']
    embed.prompt = "天气消息推送"
    # 构造内嵌消息缩略图
    thumbnail = MessageEmbedThumbnail()
    thumbnail.url = weather_dict['result']['weather_icon']
    embed.thumbnail = thumbnail
    # 构造内嵌消息fields
    embed.fields = [MessageEmbedField(name="当日温度区间：" + weather_dict['result']['temperature']),
                    MessageEmbedField(name="当前温度：" + weather_dict['result']['temperature_curr']),
                    MessageEmbedField(name="最高温度：" + weather_dict['result']['temp_high']),
                    MessageEmbedField(name="最低温度：" + weather_dict['result']['temp_low']),
                    MessageEmbedField(name="当前湿度：" + weather_dict['result']['humidity'])]

    # 通过api发送回复消息
    send = qqbot.MessageSendRequest(embed=embed, content="")
    dms_api = qqbot.AsyncDmsAPI(t_token, False)
    direct_message_guild = await dms_api.create_direct_message(CreateDirectMessageRequest(guild_id, user_id))
    await dms_api.post_direct_message(direct_message_guild.guild_id, send)
    qqbot.logger.info("/私信推送天气内嵌消息 成功")