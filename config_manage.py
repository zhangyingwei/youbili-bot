import os
import uuid

import git


class ConfigManage:

    def __init__(self):
        self.__repo_url__ = "https://github.com/zhangyingwei/youbili-bot.git"
        self.__local_repo_path__ = "./"
        self.__repo__ = git.Repo(os.path.join(self.__local_repo_path__))

    def __pull_rebase__(self):
        pass

    def __push__(self):
        self.__repo__.git.add(".")
        self.__repo__.git.commit("-m", "{}".format(uuid.uuid4()))
        self.__repo__.remote().push()


if __name__ == '__main__':
    ConfigManage().__push__()
