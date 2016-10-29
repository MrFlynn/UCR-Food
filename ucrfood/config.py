import configparser
import os.path as path


class Config(object):
    """
    Description: reading configuration file and returning compiled information from said file.
    Methods:
    - get_config_and_check : reads config file.
    - construct_url : creates the urls needed for other classes based on constructs in configuration file.
    """
    def __init__(self, filename: str, config_dir: str = './config'):
        # Initialize class variables:
        self.config_file = path.abspath(path.join(config_dir, filename))
        self.config = configparser.ConfigParser()

        # Grab configuration file and read it.
        self.get_config_and_check()

    def get_config_and_check(self, params: list):
        """
        Reads the configuration file. Checks if file exists and is not empty; returns
        exception if either check is false. Then it makes sure to check the parameters
        passed exist in the configuration file.
        """

        # Read configuration file.
        self.config.read(self.config_file)

        # Check if file exists and is not empty:
        if path.exists(self.config_file) and path.getsize(self.config_file) > 0:
            pass
        else:
            raise Exception('Configuration file does not exist.')

        # List of configuration keys.
        config_keys = []

        for section in self.config.sections():
            # Added options from configuration file. Duplicates don't matter.
            config_keys.extend(self.config.options(section))

        # Check if all parameters exist in config_keys list.
        if not set(params).isdisjoint(config_keys):
            pass
        else:
            raise Exception('Not all parameters exist in configuration file.')

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
