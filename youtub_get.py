import datetime
import os
import time
from os import rename

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import youtube_dl
import yt_dlp
import json

from config_kit import ConfigKit
from notice_bot import NoticeBot


class YoutubGet:
    def __init__(self):
        self.config = ConfigKit()
        self.options = webdriver.ChromeOptions()
        if self.config.get_bool_config("youtub", "headless"):
            self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--window-size=1920,1080")
        if self.config.get_bool_config("youtub", "use_proxy"):
            self.options.add_argument('--proxy-server={}'.format(
                self.config.get_config("youtub", "proxy_server")
            ))

        self.service = Service(
            self.config.get_config("youtub", "driver_path")
        )
        self.browser = webdriver.Chrome(
            service=self.service,
            options=self.options
        )
        self.browser.maximize_window()
        self.__init_config__()
        self.notice = NoticeBot()

    def _list_vidios(self, videos_url):
        self.browser.get(videos_url)
        tabsContent = self.browser.find_element(by=By.ID, value="tabsContent")
        tabs = tabsContent.find_elements(by=By.TAG_NAME, value="tp-yt-paper-tab")
        if len(tabs) > 2:
            tabs[1].click()
        time.sleep(1)
        contents = self.browser.find_element(By.ID, "contents")
        time.sleep(1)
        items = contents.find_element(By.ID, "items")
        time.sleep(1)
        videos = items.find_elements(by=By.TAG_NAME, value="ytd-grid-video-renderer")
        time.sleep(1)
        video_list = []
        states = self.__load_downloaded_states()
        need_download = 0
        had_download = 0
        for index, video in enumerate(videos):
            if len(video_list) >= self.config.get_int_config("youtub", "video_count_pre_account"):
                break
            video_href = video.find_element(by=By.ID, value="video-title").get_attribute("href")
            video_title = video.find_element(by=By.ID, value="video-title").text
            video_url = video_href
            if "shorts" not in video_url and "v=" in video_url:
                video_item = Video(title=video_title, url=video_url)
                if video_item.get_uuid() in states:
                    print("video had downloaded before. [{}]".format(video_item.url))
                    had_download += 1
                    continue
                video_list.append(video_item)
                need_download += 1
        print("list videos.[{}]".format(len(video_list)))
        if need_download > 0:
            self.notice.send(title="[yb]YB下载通知", content="共 {} 个视频, 下载其中的 {} 个，待下载 {} 个，有 {} 个是已经下载过.".format(len(videos),
                                                                                                          self.config.get_int_config(
                                                                                                              "youtub",
                                                                                                              "video_count_pre_account"),
                                                                                                          need_download,
                                                                                                          had_download))
        return video_list

    def __get_video_tags(self, video):
        self.browser.get(video.url)
        time.sleep(1)
        tags = self.browser.find_elements(By.TAG_NAME, "a")
        tagNames = []
        for tag in tags:
            if tag.text and tag.text.startswith("#"):
                tagNames.append(tag.text.replace("#", ""))
        video.add_tags(tagNames)

    def finish_download_hook(self, d):
        # 重命名下载的视频名称的钩子
        if d['status'] == 'finished':
            local_path = "{}/{}".format(self.config.get_config("youtub", "local_video_path"), d['filename'])
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            file_name = '{}/{}.mp4'.format(local_path, self.current_video.get_name())
            info_file_name = '{}/{}.json'.format(local_path, self.current_video.get_name())
            rename(d['filename'], file_name)
            self.__download_video_size__ = os.path.getsize(filename=file_name)
            with open(info_file_name, "w") as info_file:
                info_file.write(self.current_video.to_json())
            print('下载完成 {}'.format(file_name))
            self.__mark_downloaded(self.current_video.get_uuid())
            print("mark download state. [{}]".format(self.current_video.get_uuid()))
            try:
                print("下载缩略图")
                self.__download_proview_image(local_path)
            except:
                print("下载缩略图失败")

    def __download_proview_image(self, local_path):
        url = "https://i.ytimg.com/vi/{}/hqdefault.jpg".format(self.current_video.get_uuid())
        res = requests.get(url)
        if res.status_code == 200:
            with open('{}/{}.jpg'.format(local_path, self.current_video.get_name()), "wb") as img_file:
                img_file.write(res.content)
        else:
            print(res.content)
            raise ValueError(res.status_code)

    def __download_vedios(self, video):
        self.current_video = video
        self.__download_start_time__ = datetime.datetime.now()
        self.__download_video_size__ = 0
        ydl_ops = {
            # 'proxy': 'socks5://192.168.1.110:20170',
            'outtmpl': '%(id)s%(ext)s',
            'progress_hooks': [self.finish_download_hook],
        }
        with yt_dlp.YoutubeDL(params=ydl_ops) as ydl:
        # with youtube_dl.YoutubeDL(params=ydl_ops) as ydl:
            print("start download. [{}]".format(video.url))
            start = time.time()
            ydl.download([video.url])
            print("download finish. [{}] in [{}]".format(video.url, (time.time() - start)))

    def __load_downloaded_states(self):
        if not os.path.exists(self.__download_state_file__):
            open(self.__download_state_file__, "w").write("")
        with open(self.__download_state_file__, "r") as state_file:
            lines = []
            for line in state_file.readlines():
                lines.append(line.replace("\n", ""))
            return lines

    def __mark_downloaded(self, d_file_name):
        with open(self.__download_state_file__, "a") as state_file:
            state_file.write(d_file_name)
            state_file.write("\n")

    def start_get(self, url):
        videos = self._list_vidios(url)
        if len(videos) > 0:
            self.notice.send(title="[yb]YB下载通知", content="vcount:[{}] - url: [{}]".format(len(videos), url))
        for video in videos:
            self.__get_video_tags(video)
            print("get tags of: {tt} -> {tags}".format(tt=video.title, tags=video.tags))
            try:
                self.__download_vedios(video)
                self.notice.send("[yb]下载完成通知", "下载完成.{} \n [{}] \t 耗时: {}s \t 文件大小: {}M".format(
                    video.get_uuid(),
                    video.title,
                    (datetime.datetime.now() - self.__download_start_time__).seconds,
                    round(self.__download_video_size__/(1024*1024),3)
                ))
            except Exception as e:
                self.notice.send("[yb]告警", "下载失败.{} \n {}".format(video.title, e))

    def __init_config__(self):
        self.__download_state_file__ = self.config.get_config("youtub", "local_state")


class Video:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.uuid = url.split("v=")[1]

    def add_tags(self, tags):
        self.tags = tags

    def get_uuid(self):
        return self.uuid

    def get_name(self):
        return "v"

    def to_json(self):
        return json.dumps(self.__dict__)


if __name__ == '__main__':
    urls = []
    try:
        with open(ConfigKit().get_config("youtub", "yurl_path"), "r") as urls_file:
            for line in urls_file.readlines():
                if line not in urls:
                    urls.append(line)
        NoticeBot().send(title="[yb]信息", content="开始下载数据，共 [{}] 个URL".format(len(urls)))
        for url in urls:
            YoutubGet().start_get(url=url)
    except Exception as e:
        NoticeBot().send("[yb]告警", "YB启动失败.{}".format(e))
