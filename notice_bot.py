import requests

from notice_dingding import NoticeDingDing


class NoticeBot:
    def __init__(self):
        self.notice_client = NoticeDingDing()

    def send(self,title,content):
        # self.url = "https://sctapi.ftqq.com/SCT150172TjXj2nd6es5NN8j05X0jobjj1.send?title={messagetitle}&desp={messagecontent}".format(
        #     messagetitle=title,
        #     messagecontent=content
        # )
        # resp = requests.get(url=self.url)
        # TODO
        resp = f"{title},{content}"
        # resp = self.notice_client.send(title=title,content=content)
        print("notice result: {}".format(resp))

