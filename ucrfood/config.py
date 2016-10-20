import configparser
import os.path as path


class Config(object):
    def __init__(self, filename):
        self.config_file = path.abspath(path.join('../config', filename))
        self.config = configparser.ConfigParser()

    def get_config(self):
        self.config.read(self.config_file)

    def construct_url(self):
        urls = []

        for section in self.config.sections():
            if section == 'DEFAULT':
                continue
            else:
                url_base = self.config['DEFAULT']['BaseURL']
                location_num = self.config[section]['LocationNum']
                location_name = self.config[section]['LocationName']

                return urls.append(url_base + location_num + location_name)