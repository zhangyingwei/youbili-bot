import os
import time
from os import rename

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import youtube_dl
import json

from notice_bot import NoticeBot


class YoutubGet:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--window-size=1920,1080")
        # self.options.add_argument('--proxy-server=http://192.168.1.110:20171')

        self.service = Service("/opt/youbili-bot/driver/chromedriver")
        # self.service = Service("E:\\codes\\youbili-bot\\driver\\chromedriver.exe")
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
        for index, video in enumerate(videos):
            if len(video_list) >= 2:
                break
            video_href = video.find_element(by=By.ID, value="video-title").get_attribute("href")
            video_title = video.find_element(by=By.ID, value="video-title").text
            video_url = video_href
            if "shorts" not in video_url and "v=" in video_url:
                video_item = Video(title=video_title, url=video_url)
            if video_item.get_uuid() in states:
                print("video had downloaded before. [{}]".format(video_item.url))
                continue
            video_list.append(video_item)
        print("list videos.[{}]".format(len(video_list)))
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
            local_path ="video/{}".format(d['filename'])
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            file_name = '{}/{}.mp4'.format(local_path,self.current_video.get_name())
            info_file_name = '{}/{}.json'.format(local_path,self.current_video.get_name())
            rename(d['filename'], file_name)
            with open(info_file_name,"w") as info_file:
                info_file.write(self.current_video.to_json())
            print('下载完成 {}'.format(file_name))
            self.__mark_downloaded(self.current_video.get_uuid())
            print("mark download state. [{}]".format(self.current_video.get_uuid()))
            try:
                print("下载缩略图")
                self.__download_proview_image(local_path)
            except:
                print("下载缩略图失败")

    def __download_proview_image(self,local_path):
        url = "https://i.ytimg.com/vi/{}/hqdefault.jpg".format(self.current_video.get_uuid())
        res = requests.get(url)
        if res.status_code == 200:
            with open('{}/{}.jpg'.format(local_path,self.current_video.get_name()),"wb") as img_file:
                img_file.write(res.content)
        else:
            print(res.content)
            raise ValueError(res.status_code)

    def __download_vedios(self,video):
        self.current_video = video
        ydl_ops = {
            # 'proxy': 'socks5://192.168.1.110:20170',
            'outtmpl': '%(id)s%(ext)s',
            'progress_hooks': [self.finish_download_hook],
        }
        with youtube_dl.YoutubeDL(params=ydl_ops) as ydl:
            print("start download. [{}]".format(video.url))
            start = time.time()
            ydl.download([video.url])
            print("download finish. [{}] in [{}]".format(video.url,(time.time() - start)))

    def __load_downloaded_states(self):
        if not os.path.exists(self.__download_state_file__):
            open(self.__download_state_file__,"w").write("")
        with open(self.__download_state_file__,"r") as state_file:
            lines = []
            for line in state_file.readlines():
                lines.append(line)
            return lines

    def __mark_downloaded(self, d_file_name):
        with open(self.__download_state_file__,"w") as state_file:
            state_file.writelines([d_file_name])

    def start_get(self,url):
        videos = self._list_vidios(url)
        for video in videos:
            self.__get_video_tags(video)
            print("get tags of: {tt} -> {tags}".format(tt=video.title, tags=video.tags))
            try:
                self.__download_vedios(video)
                self.notice.send("[yb]通知","下载完成.{} \n {}".format(video.get_uuid(), video.title))
            except Exception as e:
                self.notice.send("[yb]告警","下载失败.{} \n {}".format(video.title,e))

    def __init_config__(self):
        self.__download_state_file__ = "d_state.txt"


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
    urls = [
        "https://www.youtube.com/c/Kavsoft/videos",
        "https://www.youtube.com/c/PaulHudson/videos",
        "https://www.youtube.com/c/iOSAcademy/videos",
        "https://www.youtube.com/channel/UCHaYcy9627HPl6YTwKrYBAw/videos"
    ]
    for url in urls:
        YoutubGet().start_get(url=url)

