from configparser import ConfigParser


class ConfigKit:
    def __init__(self):
        self.__config_path__ = "conf.ini"
        self.__cf__ = ConfigParser()
        self.__cf__.read(self.__config_path__)
        self.__env_profile__ = self.__cf__.get("env", "profile")

    def get_config(self, section, key):
        env_section = "{}-{}".format(
            self.__env_profile__,section
        )
        res =  self.__cf__.get(section=env_section, option=key)
        print("get config:{} -> {}".format([env_section,key],res))
        return  res

    def get_bool_config(self, section, key):
        env_section = "{}-{}".format(
            self.__env_profile__, section
        )
        res = self.__cf__.getboolean(section=env_section, option=key)
        print("get config:{} -> {}".format([env_section, key], res))
        return res

    def get_int_config(self, section, key):
        env_section = "{}-{}".format(
            self.__env_profile__, section
        )
        res = self.__cf__.getint(section=env_section, option=key)
        print("get config:{} -> {}".format([env_section, key], res))
        return res

if __name__ == '__main__':
    config = ConfigKit()
    print(
        config.get_config("youtub", "driver_path")
    )
