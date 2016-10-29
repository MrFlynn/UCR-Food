import configparser
import os.path as path


class Config(object):
    """
    Description: reading configuration file and returning compiled information from said file.
    Methods:
    - get_config : reads config file.
    - construct_url : creates the urls needed for other classes based on constructs in configuration file.
    """
    def __init__(self, filename: str, config_dir: str = './config'):
        # Initialize class variables:
        self.config_file = path.abspath(path.join(config_dir, filename))
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
        """
        Turns configuration file into dict with mirrored structure. Structure will look like this:
        {section_name: {key_1: key_val, ...}, ...}

        The first loop goes through and finds each section. The inner loop takes each section and grabs each
        key from said respective section. NOTE: A section named [DEFAULT] will result in each section
        containing everything that was in the [DEFAULT] section.
        """

        # Main dictionary for config file.
        config_dict = {}

        for config_section in self.config.sections():

            # Dict for each configuration section.
            section_dict = {}

            for key in self.config[config_section]:
                # Added config_section data to section_dict
                section_dict[key] = self.config[config_section][key]

            # Append section_dict to config_dict
            config_dict[config_section] = section_dict

        return config_dict
