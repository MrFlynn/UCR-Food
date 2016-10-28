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
        self.config_file = path.abspath(path.join('./config', filename))
        self.config = configparser.ConfigParser()

        # Grab configuration file and read it.
        self.get_config()

    def get_config(self):
        """
        Reads the configuration file.

        NOTE: this is only in a separate method because I want to be able to load the file and run logic on
        it separately.
        """

        self.config.read(self.config_file)

    def construct_dict(self) -> dict:

        config_dict = {}

        for config_section in self.config.sections():

            section_dict = {}

            for key in self.config[config_section]:
                section_dict[key] = self.config[config_section][key]

            config_dict[config_section] = output2

        return config_dict
