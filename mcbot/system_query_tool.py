import psutil
from botpy import logging

# Test
# print(psutil.cpu_percent(interval=1))
# print(psutil.virtual_memory().percent)
# print(psutil.swap_memory().percent)
# print(psutil.disk_usage('C:/').percent)


_log = logging.get_logger()


class SystemStat:
    def query_system_stats_aio(self, interval=1, path='~'):
        try:
            cpu_percent = psutil.cpu_percent(interval=interval)+'%'
            mem_percent = psutil.virtual_memory().percent+'%'
            swp_percent = psutil.swap_memory().percent+'%'
            dsk_percent = psutil.disk_usage(path=path).percent+'%'

            msg = f"\nCPU占用：{cpu_percent}\n内存占用：{mem_percent} （swap占用：{swp_percent}）\n硬盘占用：{dsk_percent}\n"

            return msg
        except Exception as e:
            _log.error(f"[{self.__class__.__name__}] {e}")
            return '读取硬件信息出错'
