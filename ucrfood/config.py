import configparser
import os.path as path


class Config(object):
    """
    Description: reading configuration file and returning compiled information from said file.
    Methods:
    - get_config : reads config file.
    - construct_url : creates the urls needed for other classes based on constructs in configuration file.
    """
    def __init__(self, filename):
        # Initialize class variables:
        self.config_file = path.abspath(path.join('../config', filename))
        self.config = configparser.ConfigParser()

        # Grab configuration file and read it.
        self.get_config()

    def get_config(self):
        """
        Reads the configuration file.

        NOTE: this is only in a separate method because I want to be able to load the file and run logic on it
        separately.
        """

        self.config.read(self.config_file)

    def construct_url(self):
        """
        Gets the sections from the configuration file, and gets the requisite data from each to create the url w/o the
        dtdate object.
        """

        # List of urls.
        urls = []

        for section in self.config.sections():
            if section == 'DEFAULT':
                continue
            else:
                url_base = self.config['DEFAULT']['BaseURL']
                location_num = self.config[section]['LocationNum']
                location_name = self.config[section]['LocationName']

                urls.append(url_base + location_num + location_name)

        return urls
