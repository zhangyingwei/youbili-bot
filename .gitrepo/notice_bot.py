import requests

class NoticeBot:
    def __init__(self):
        pass

    def send(self,title,content):
        self.url = "https://sctapi.ftqq.com/SCT150172TjXj2nd6es5NN8j05X0jobjj1.send?title={messagetitle}&desp={messagecontent}".format(
            messagetitle=title,
            messagecontent=content
        )
        resp = requests.get(url=self.url)
        print("notice result: {}".format(resp.text))

