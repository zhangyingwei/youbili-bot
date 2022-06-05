import json
import os
import random
import shutil
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from config_kit import ConfigKit
from notice_bot import NoticeBot


class BiliUpload:

    def __init__(self):
        self.config = ConfigKit()
        self.options = webdriver.ChromeOptions()
        if self.config.get_bool_config("bili", "headless"):
            self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--window-size=1920,1080")

        self.service = Service(
            self.config.get_config("youtub", "driver_path")
        )
        self.browser = webdriver.Chrome(
            service=self.service,
            options=self.options
        )
        # self.browser.maximize_window()
        self.__init_config__()
        self.notice = NoticeBot()

    def __init_config__(self):
        self.__cookie_file__ = self.config.get_config("bili", "cookie_file")
        self.__videos_dir__ = self.config.get_config("bili", "local_video_path")
        self.__cookie_seted__ = False
        self.__is_debug__ = self.config.get_bool_config("bili","isDebug")

    def __open_createor_platform(self):
        self.browser.get("https://member.bilibili.com/platform/home")
        print("打开浏览器")
        if not self.__cookie_seted__:
            cookies = self.__get_cookie()
            for cookie in cookies:
                print("add cookie:{}".format(cookie))
                self.browser.add_cookie(cookie)
        print("设置 Cookie")
        print("打开创作中心")
        self.browser.get("https://member.bilibili.com/platform/home")
        if not self.__cookie_seted__:
            new_cookie = self.browser.get_cookies()
            self.__store_cookie(new_cookie)
            print("保存最新 Cookie")
            self.__cookie_seted__ = True
        time.sleep(2)
        try:
            print("跳过引导页")
            self.browser.find_element(By.ID, "canvas-wrap").find_element(By.CLASS_NAME, "jump").click()
        except:
            pass
        print("打开上传页面")
        try:
            self.browser.find_element(By.ID, "nav_upload_btn").click()
        except:
            self.notice.send(title="[yb]告警", content="未发现上传视频按钮，可能是登录失败，Cookie 失效")
        time.sleep(1)
        try:
            print("打开上传视频标签页")
            self.browser.find_element(By.CLASS_NAME, "upload-nav").find_elements(By.CLASS_NAME, "upload-nav-item")[
                0].click()
        except:
            pass
        time.sleep(2)

    def start(self):
        # self.__open_createor_platform()
        # self.__upload_video()
        self.__list_videos()

    def __list_videos(self):
        if self.__is_debug__:
            self.notice.send(title="[yb]发布提示", content="我已经迫不及待了...")
        count = 0
        for vitem in os.listdir(self.__videos_dir__):
            info_path = os.path.join(self.__videos_dir__, vitem, "v.json")
            video_path = os.path.join(self.__videos_dir__, vitem, "v.mp4")
            img_path = os.path.join(self.__videos_dir__, vitem, "v.jpg")
            done_path = os.path.join(self.__videos_dir__, vitem, "done")
            print("检查 {}".format(done_path))
            if os.path.exists(done_path):
                continue
            with open(info_path, "r") as info_file:
                info = json.load(info_file)
                if self.__is_debug__:
                    print("开始处理视频: [{}]".format(info["title"]))
                try:
                    self.__open_createor_platform()
                    self.__upload_video(vpath=os.path.abspath(video_path), vtitle=info["title"], vtags=info["tags"],
                                        imgpath=img_path)
                    time.sleep(2)
                except Exception as e:
                    print("处理视频失败. {}".format(e))
                    self.__mark_uploaded(video_path)
                    self.__mark_faild(video_path,e)
                    self.notice.send(title="[yb]视频处理通知", content="处理视频失败. {}".format(e))
                    count -= 1
                    time.sleep(30)
            count += 1
        self.notice.send(title="[yb]发布通知", content="共发布了 {} 个视频".format(count))

    def __store_cookie(self, cookies):
        print(cookies)
        cookie_str = ""
        for cookie in cookies:
            print("store cookie: {}".format(cookie))
            cookie_str += "{key}={value};".format(key=cookie["name"], value=cookie["value"])
        print("new cookid string: {}".format(cookie_str))
        with open(self.__cookie_file__, "w") as cookie_file:
            cookie_file.write(cookie_str)

    def __get_cookie(self):
        if not os.path.exists(self.__cookie_file__):
            print("cookie file is not exites[{}]".format(self.__cookie_file__))
            self.notice.send(title="[yb]告警", content="cookie file is not exites[{}]".format(self.__cookie_file__))
            exit(-1)
        with open(self.__cookie_file__, "r") as cookie_file:
            cookie_content = cookie_file.read()
            items = cookie_content.split(";")
            cookie_dict = []
            for item in items:
                if "=" in item:
                    kv = item.split("=")
                    dict_item = {"name": kv[0].strip(), "value": kv[1].strip(), 'domain': '.bilibili.com'}
                    cookie_dict.append(dict_item)
            return cookie_dict

    def __upload_video(self, vpath, vtitle, vtags, imgpath):
        print("start upload video: {}".format(vtitle))
        print("切换 iframe")
        self.browser.switch_to.frame("videoUpload")
        print("上传视频")
        self.browser.find_element(By.CLASS_NAME, "bcc-upload-wrapper").find_element(By.TAG_NAME, "input").send_keys(
            vpath)

        title = vtitle
        time.sleep(1)

        print("填写 title")
        title_input = self.browser.find_element(By.CLASS_NAME, "video-title").find_element(By.TAG_NAME, "input")
        title_input.send_keys(Keys.CONTROL + 'a')
        title_input.send_keys(Keys.BACKSPACE)
        title_input.send_keys(title)

        time.sleep(1)

        print("选择视频类型为 自制")
        # 自制-0  转载-1
        try:
            self.browser.find_element(By.CLASS_NAME, "type-check-radio-wrp") \
                .find_elements(By.CLASS_NAME, "check-radio-v2-container")[0].click()
        except Exception as e:
            print("选择视频类型失败. {}".format(e))

        time.sleep(1)

        try:
            print("选择视频分类")
            vtype = self.browser.find_element(By.CLASS_NAME, "video-type")
            vtype.find_element(By.CLASS_NAME, "select-container").click()
            drop_container = self.browser.find_element(By.CLASS_NAME, "drop-container")
            drop_container.find_element(By.CLASS_NAME, "drop-f-wrp").find_elements(By.CLASS_NAME, "drop-f-item")[
                4].click()
            drop_container.find_element(By.CLASS_NAME, "drop-t-wrp").find_elements(By.CLASS_NAME, "drop-t-item")[
                7].click()
        except Exception as e:
            print("select type error.{}".format(e))

        tags = vtags
        tags.append("知识分享")
        print("添加标签")
        tag_container = self.browser.find_element(By.CLASS_NAME, "tag-container")
        for tag in tags:
            print("add tag: {}".format(tag))
            tag_container.find_element(By.TAG_NAME, "input").send_keys(tag)
            tag_container.find_element(By.TAG_NAME, "input").send_keys(Keys.ENTER)
            time.sleep(2)

        try:
            print("检测是否上传完成")
            self.__check_finish()

            time.sleep(2)
            if os.path.exists(imgpath):
                try:
                    print("修正封面图大小")
                    new_img_path = "{}.n.jpg".format(imgpath)
                    img = Image.open(imgpath)
                    nimg = img.resize((1146, 717))
                    print(nimg.size)
                    nimg.save(new_img_path)
                    print("上传封面图")
                    self.browser.find_element(By.CLASS_NAME, "bcc-upload-wrapper").find_element(By.TAG_NAME,
                                                                                                "input").send_keys(
                        os.path.abspath(new_img_path)
                    )
                    time.sleep(2)
                    self.browser.find_element(By.CLASS_NAME, "prize-dialog-footer").find_element(By.CLASS_NAME,
                                                                                                 "bcc-button--primary").click()
                    time.sleep(2)
                except Exception as e:
                    print("上传封面图失败 - {}".format(e))

            print("点击提交按钮")
            self.browser.execute_script("var q=document.body.scrollTop=1000")
            time.sleep(2)
            try:
                self.browser.find_element(By.CLASS_NAME, "submit-container").find_element(By.CLASS_NAME,
                                                                                          "submit-add").click()
            except:
                self.browser.execute_script('document.getElementsByClassName("submit-add")[0].click()')

            print("publish clicked. [{}]".format(vtitle))
            self.__check_success(vtitle, vpath)
            # TODO
            # time.sleep(10000)
            sleep_time = random.randint(60,180)
            print("random sleep.{}".format(sleep_time))
            time.sleep(sleep_time)

        except Exception as e:
            print("publish faild,{}".format(e))
            self.notice.send(title="[yb]告警", content="发布视频失败. {} - {}".format(vtitle, e))

    def __mark_uploaded(self, vpath):
        with open(os.path.join(os.path.dirname(vpath), "done"), "w") as done_file:
            done_file.write("")

    def __mark_faild(self, vpath, e):
        with open(os.path.join(os.path.dirname(vpath), "faild_msg"), "w") as done_file:
            done_file.write("{}".format(e))

    def __check_finish(self):
        status = self.browser.find_element(By.CLASS_NAME, "file-status-text").text
        while "完成" not in status and "失败" not in status:
            time.sleep(5)
            print("check status...[{}]".format(status))
            status = self.browser.find_element(By.CLASS_NAME, "file-status-text").text
        print("等待10秒，生成封面图.")
        time.sleep(10)

    def __check_success(self, vtitle, vpath):
        count = 10
        for i in range(count):
            try:
                texts = self.browser.find_element(By.CLASS_NAME, "step-des")
                console_log = self.browser.get_log("browser")
                print("check success. {} - {}".format(texts, console_log))
                for log in console_log:
                    print("console: {}".format(log))
                    if log['message'] and "tag" in log['message']:
                        continue
                    if log['message'] and "相同标题的稿件" in log['message']:
                        self.__mark_uploaded(vpath)
                        if self.__is_debug__:
                            self.notice.send(title="[yb]通知", content="重复视频，跳过. {}".format(vtitle))
                        return
                    elif log['message'] and "Error" in log['message']:
                        print("控制台错误. {}".format(log))
                        # print("发布视频失败. {} - {}".format(vtitle, "控制台错误"))
                        # self.notice.send(title="[yb]告警", content="发布视频失败. {} - {} - {}".format(vtitle, "控制台错误",console_log))
                        # return
                if "成功" in texts.text:
                    print("标记视频为已处理")
                    self.__mark_uploaded(vpath)
                    if self.__is_debug__:
                        self.notice.send(title="[yb]通知", content="发布视频成功. {}".format(vtitle))
                    print("发布视频成功. {}".format(vtitle))
                    self.__remove_after_publish__(vpath)
                    return
                time.sleep(2)
            except Exception as e:
                print("发布成功检测: {}".format(e))
                time.sleep(2)
        self.browser.get_screenshot_as_file(
            os.path.abspath("{}.screenshot.png".format(vpath))
        )
        print("发布视频失败. {} - {}".format(vtitle, "未检测到成功标识"))
        self.notice.send(title="[yb]告警", content="发布视频失败. {} - {}".format(vtitle, "未检测到成功标识"))

    def __remove_after_publish__(self, vpath):
        dir_path = os.path.dirname(vpath)
        shutil.rmtree(dir_path)
        # self.notice.send(title="")
        # for file in os.listdir(dir_path):
        #     file_path = os.path.join(dir_path,file)
        #


if __name__ == '__main__':
    try:
        BiliUpload().start()
    except Exception as e:
        NoticeBot().send(title="[yb]告警", content="BI 启动失败. {}".format(e))
