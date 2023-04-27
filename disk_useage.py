import psutil
from notice_bot import NoticeBot

if __name__ == '__main__':
    notice = NoticeBot()
    # 获取硬盘占用量
    disk_usage = psutil.disk_usage('/')

    # 打印总容量、已用容量和可用容量
    print('总容量：', disk_usage.total)
    print('已用容量：', disk_usage.used)
    print('可用容量：', disk_usage.free)
    print('使用率：', disk_usage.used/disk_usage.total)
    if disk_usage.used / disk_usage.total > 0.8:
        notice.send(title="[yb]硬盘告警",
                     content="硬盘容量:{} \n目前已使用:{} \n剩余可用:{} \n使用率:{}".format(
                         disk_usage.total,
                         disk_usage.used,
                         disk_usage.free,
                         disk_usage.used / disk_usage.total
                     ))


def is_disk_full():
    disk_usage = psutil.disk_usage('/')
    if disk_usage.used / disk_usage.total > 0.8:
        return True
    return False