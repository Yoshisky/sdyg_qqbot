import configparser
import socket
import re
import os
from mcstatus import JavaServer
from botpy import logging

_log = logging.get_logger()
config = configparser.ConfigParser()
try:
    config.read('config.cfg','UTF-8')
except Exception as e:
    _log.error(f"[init] {e}")

class Mcstatus():
    def query_online_players(self, server='localhost:25565'):
        try:
            server_status = JavaServer.lookup(server)
            status = server_status.status()
            return f'{status.players.online}/{status.players.max}, {int(status.latency)}ms'
        except ConnectionRefusedError as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            return "GG"
        except socket.timeout as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            return "X"
        except socket.gaierror as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            return "?"
        except Exception as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            return  "Error"

    def query_detail(self, server='localhost:25565'):
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

            # url not allowed on api calling
            msg += f"连接名称(。换为.): {server.replace('.','。')}"
            msg += f"\nMC版本: v{response.version.name} (protocol {response.version.protocol})"
            msg += f'\n服务器描述: "{response.description}"'
            msg += f"\n玩家: {response.players.online}/{response.players.max} {player_sample}"
            msg += f"\n延迟: {int(response.latency)}ms"

            return msg

        except ConnectionRefusedError as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            msg += "服务器拒绝访问，多半是寄啦！"
            return msg
        except socket.timeout as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            msg += "连接服务器超时，或者主机格式有误"
            return msg
        except socket.gaierror as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            msg += "未知域名"
            return msg
        except Exception as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            msg += "未知错误"
            return msg

    def query_saves(self, command='/downloads'):
        msg = ''
        try:
            if re.match('^/downloads\s*$', command):
                msg += f'历史存档下载地址：{config.get("server","download_link").replace(".","。")}'
                saves = len(os.listdir(f'{config.get("server","saves_dir")}')) - config.getint('server','saves_dir_exclusive')  # minus saves_dir_exclusive
                msg += '\n当前共有{}个存档，输入"/downloads <包名>"快速查询存档下载链接'.format(saves)

            else:
                if command.startswith('/downloads '):
                    modpack = command.replace('/downloads ', '')
                elif command.startswith('/downloads'):
                    modpack = command.replace('/downloads','')

                saves = os.listdir(f'{config.get("server","saves_dir")}')
                # 'find == -1' means find nothing
                results = [x for i, x in enumerate(saves) if x.find(modpack) != -1]

                if len(results) >= 10:
                    msg += '查询整合包{}的存档结果过多'.format(modpack)
                elif len(results) > 0:
                    msg += '整合包{}的存档下载地址为：'.format(modpack)
                    for result in results:
                        msg += f'\n{config.get("server","download_link")}' + result
                else:
                    msg += '查不到整合包{}的存档'.format(modpack)
        except Exception as e:
            msg += '乐，出现未知错误'
            _log.error(f"[{self.__class__.__name__}] {e}")

        return msg
