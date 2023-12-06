import json
import os
import re
import socket
import time

from sanic import Sanic
from mcstatus import JavaServer


app = Sanic('sdyg_qqbot')
base_path = "/mnt/minecraft/go-cqhttp/sdyg_qqbot/nonebot/keyword/"


@app.websocket('/sdyg_qqbot')
async def qqbot(request, ws):
    """QQ机器人"""
    while True:
        data = await ws.recv()
        data = json.loads(data)
        print(json.dumps(data, indent=4, ensure_ascii=False))
        # if 判断是群消息且文本消息不为空
        if data.get('message_type') == 'group' and data.get('raw_message'):
            raw_message = data['raw_message']
            if raw_message == "#help":
                try:
                    with open(base_path + "commands.txt", encoding="utf8") as f:
                        msg = f.read()
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#list":
                msg = ""
                try:
                    server = "localhost:25565"
                    online = query_online_players(server)

                    msg += f"1服在线玩家：{online}\n"

                    server = "localhost:23333"
                    online = query_online_players(server)

                    msg += f"2服在线玩家：{online}\n"

                    server = "localhost:23335"
                    online = query_online_players(server)

                    msg += f"3服在线玩家：{online}\n"

                    server = "localhost:23337"
                    online = query_online_players(server)

                    msg += f"4服在线玩家：{online}\n"

                    server = "localhost:23330"
                    online = query_online_players(server)

                    msg += f"5服在线玩家：{online}\n"
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#1":
                msg = "1服情况：\n"
                try:
                    server = "xxnode.bupt.moe:25565"

                    msg += query_detail(server)

                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#2":
                msg = "2服情况：\n"
                try:
                    server = "xxnode.bupt.moe:23333"

                    msg += query_detail(server)

                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#3":
                msg = "3服情况：\n"
                try:
                    server = "xxnode.bupt.moe:23335"

                    msg += query_detail(server)

                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#4":
                msg = "4服情况：\n"
                try:
                    server = "xxnode.bupt.moe:23337"

                    msg += query_detail(server)

                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif raw_message == "#5":
                msg = "5服情况：\n"
                try:
                    server = "www.sdyg.games:25565"

                    msg += query_detail(server)

                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif str(raw_message).startswith('#status'):
                msg = ''
                try:
                    server = str(raw_message).replace('#status', '').replace(' ', '')
                    if server != '':
                        msg += query_detail(server)

                        ret = {
                            'action': 'send_group_msg',
                            'params': {
                                'group_id': data['group_id'],
                                'message': msg,
                            }
                        }
                        await ws.send(json.dumps(ret))
                    else:
                        msg += '输入 "#status [主机:端口]" 查询其他服务器'

                        ret = {
                            'action': 'send_group_msg',
                            'params': {
                                'group_id': data['group_id'],
                                'message': msg,
                            }
                        }
                        await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            elif str(raw_message).startswith('#downloads'):
                msg = ''
                try:
                    if re.match('^#downloads$', str(raw_message)):
                        msg += '历史存档下载地址：*Encrypted*'
                        saves = len(os.listdir('../../legacy_saves/')) - 1  # minus LATEST_UPDATE
                        msg += '\n当前共有{}个存档，输入"#downloads <包名>"快速查询存档下载链接'.format(saves)
                        ret = {
                            'action': 'send_group_msg',
                            'params': {
                                'group_id': data['group_id'],
                                'message': msg,
                            }
                        }
                        await ws.send(json.dumps(ret))
                    else:
                        modpack = str(raw_message).replace('#downloads ', '')
                        saves = os.listdir('../../legacy_saves/')
                        results = [x for i, x in enumerate(saves) if x.find(modpack) != -1]

                        if len(results) >= 10:
                            msg += '查询整合包{}的存档结果过多'.format(modpack)
                        elif len(results) > 0:
                            msg += '整合包{}的存档下载地址为：'.format(modpack)
                            for result in results:
                                msg += '\nhttps://baidu.com' + result
                        else:
                            msg += '查不到整合包{}的存档'.format(modpack)

                        ret = {
                            'action': 'send_group_msg',
                            'params': {
                                'group_id': data['group_id'],
                                'message': msg,
                            }
                        }
                        await ws.send(json.dumps(ret))
                except Exception as e:
                    msg += '乐，出现未知错误'
                    ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                    await ws.send(json.dumps(ret))

            # else:
            #     msg = "输入 #help 查看所有命令，间隔60s"
            #     ret = {
            #         'action': 'send_group_msg',
            #         'params': {
            #             'group_id': data['group_id'],
            #             'message': msg,
            #         }
            #     }
            #     await ws.send(json.dumps(ret))
            #     time.sleep(1)

            """
            elif raw_message == "/群主介绍":
                with open(base_path + "群主介绍.txt", encoding="utf8") as f:
                    msg = f.read()
                ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                await ws.send(json.dumps(ret))
            elif raw_message == "/群主主页":
                with open(base_path + "群主主页.txt", encoding="utf8") as f:
                    msg = f.read()
                ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                await ws.send(json.dumps(ret))
            elif raw_message == "/Python学习目录":
                with open(base_path + "Python学习目录.txt", encoding="utf8") as f:
                    msg = f.read()
                ret = {
                        'action': 'send_group_msg',
                        'params': {
                            'group_id': data['group_id'],
                            'message': msg,
                        }
                    }
                await ws.send(json.dumps(ret))
            elif raw_message == "/开发项目":
                with open(base_path + "开发项目.txt", encoding="utf8") as f:
                    msg = f.read()
                ret = {
                    'action': 'send_group_msg',
                    'params': {
                        'group_id': data['group_id'],
                        'message': msg,
                    }
                }
                await ws.send(json.dumps(ret))
            """


def query_online_players(server):
    try:
        server_status = JavaServer.lookup(server)
        status = server_status.status()
        return status.players.online
    except ConnectionRefusedError:
        return "GG"
    except socket.timeout:
        return "X"
    except socket.gaierror:
        return "?"


def query_detail(server):
    msg = ""
    try:
        # try:
        #     mcserver = JavaServer.lookup(server)
        #     resp = mcserver
        #     response = mcserver.query()
        #
        # except socket.timeout:
        #     msg += (
        #         "The server did not respond to the query protocol."
        #         "\nPlease ensure that the server has enable-query turned on,"
        #         " and that the necessary port (same as server-port unless query-port is set) is open in any firewall(s)."
        #         "\nSee https://wiki.vg/Query for further information."
        #     )
        #     return msg
        # msg += f"host: {response.raw['hostip']}:{response.raw['hostport']}"
        # msg += f"\nsoftware: v{response.software.version} {response.software.brand}"
        # msg += f"\nplugins: {response.software.plugins}"
        # msg += f'\nmotd: "{response.motd}"'
        # msg += f"\nplayers: {response.players.online}/{response.players.max} {response.players.names}"

        server_status = JavaServer.lookup(server)
        response = server_status.status()
        # if response.players.sample is not None:
        #     player_sample = str([f"{player.name} ({player.id})" for player in response.players.sample])
        # else:
        #     player_sample = "No players online"
        #
        # msg += f"version: v{response.version.name} (protocol {response.version.protocol})"
        # msg += f'\ndescription: "{response.description}"'
        # msg += f"\nplayers: {response.players.online}/{response.players.max} {player_sample}"
        if response.players.sample is not None:
            # player_sample = str([f"{player.name} ({player.id})" for player in response.players.sample])
            player_sample = str([f"{player.name}" for player in response.players.sample])
        else:
            player_sample = "没有玩家在线"

        msg += f"连接名称: {server}"
        msg += f"\nMC版本: v{response.version.name} (protocol {response.version.protocol})"
        msg += f'\n服务器描述: "{response.description}"'
        msg += f"\n玩家: {response.players.online}/{response.players.max} {player_sample}"

        return msg

    except ConnectionRefusedError:
        msg += "服务器拒绝访问，多半是寄啦！"
        return msg
    except socket.timeout:
        msg += "连接服务器超时，或者主机格式有误"
        return msg
    except socket.gaierror:
        msg += "未知域名"
        return msg


if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True, port=8765, auto_reload=True)
