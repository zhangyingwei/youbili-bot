import os
import shutil
import time
from notice_bot import NoticeBot


class ConfigManage:
    def __init__(self):
        self.__base_path = "E:\\codes\\youbili-bot"
        self.__repo_url__ = "https://github.com/zhangyingwei/youbili-bot.git"
        self.__local_repo_path__ = ".gitrepo"
        self.notice = NoticeBot()

        if os.path.exists(os.path.join(self.__base_path, self.__local_repo_path__)):
            self.clear()
        os.makedirs(
            os.path.join(self.__base_path, self.__local_repo_path__)
        )
        os.chdir(os.path.join(self.__base_path, self.__local_repo_path__))

    def __run_cmd__(self, cmd):
        os.system(cmd)

    def push(self):
        cmd_add = "git add ."
        cmd_commit = "git commit -m '{}'".format(time.time())
        self.__run_cmd__(cmd_add)
        self.__run_cmd__(cmd_commit)

    def clone(self):
        try:
            cmd = "git clone {} {}".format(self.__repo_url__, os.path.join(
                self.__base_path, self.__local_repo_path__
            ))
            self.__run_cmd__(cmd)
        except Exception as e:
            self.notice.send(title="[yb]CM 告警", content="clone error \n {}".format(e))
        time.sleep(2)

    def replace_yurls(self):
        shutil.copyfile(os.path.join(
            self.__base_path, self.__local_repo_path__, "yurls.txt"
        ), os.path.join(self.__base_path, "yurls.txt"))

    def replace_cookie(self):
        shutil.copyfile(os.path.join(
            self.__base_path, self.__local_repo_path__, "cookie.txt"
        ), os.path.join(self.__base_path, "cookie.txt"))

    def upload_state(self):
        shutil.copyfile(
            os.path.join(self.__base_path, "d_state.txt"),
            os.path.join(self.__base_path, self.__local_repo_path__, "d_state.txt")
        )

    def clear(self):
        time.sleep(2)
        try:
            shutil.rmtree(
                os.path.join(
                    self.__base_path, self.__local_repo_path__
                )
            )
        except Exception as e:
            self.notice.send(title="[yb]CM 告警", content="clear error \n {}".format(e))


if __name__ == '__main__':
    cm = ConfigManage()
    cm.clone()
    cm.replace_yurls()
    cm.replace_cookie()
    cm.upload_state()
    cm.push()
    cm.clear()
