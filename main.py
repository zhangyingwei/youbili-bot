from bilibili_upload import BiliUpload
from youtub_get import YoutubGet

if __name__ == '__main__':
    urls = [
        "https://www.youtube.com/c/Kavsoft/videos",
        "https://www.youtube.com/c/PaulHudson/videos",
        "https://www.youtube.com/c/iOSAcademy/videos",
        "https://www.youtube.com/channel/UCHaYcy9627HPl6YTwKrYBAw/videos"
    ]
    for url in urls:
        try:
            YoutubGet().start_get(url=url)
        except Exception as e:
            print("youtube get error. {} -{} ".format(url, e))
    BiliUpload().start()
