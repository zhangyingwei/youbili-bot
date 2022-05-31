import json
import requests


class NoticeDingDing:
    def __init__(self):
        self.__webhook__ = "https://oapi.dingtalk.com/robot/send?access_token=a4c747005162c5f49f3ddbddb9972d40311672ed320ab6e958fed50780a01721"

    def send(self, title, content):
        program = {
            "msgtype": "markdown",
            "markdown": {"title": title,"text": "# {}\n{}".format(title,content)},
        }
        headers = {'Content-Type': 'application/json'}
        f = requests.post(self.__webhook__, data=json.dumps(program), headers=headers)
        return f.text


if __name__ == '__main__':
    NoticeDingDing().send(title="[yb]asdf",content="[yb]asdfasdfafd")