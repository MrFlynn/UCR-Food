import configparser
import os.path as path
from collections import OrderedDict


class Config(object):
    """
    Description: reading configuration file and returning compiled information from said file.
    Methods:
    - _check_against_config : reads configuration file and performs various tests on file.
    - construct_url : creates the urls needed for other classes based on constructs in configuration file.
    """
    def __init__(self, filename: str, config_dir: str = './config'):
        # Initialize class variables:
        self.config_file_path = path.abspath(path.join(config_dir, filename))
        self.config_file = filename
        self.config = configparser.ConfigParser()

        # Read configuration file:
        self.config.read(self.config_file_path)

        # Config dict:
        self.config_dict = None

    def _check_against_config(self, params: list):
        """
        Reads the configuration file. Checks if file exists and is not empty; returns
        exception if either check is false. Then it makes sure to check the parameters
        passed exist in the configuration file.
        """

        # Make passed parameter list lowercase.
        _params = [opt.lower() for opt in params]

        # Check if file exists and is not empty:
        if path.exists(self.config_file_path) and path.getsize(self.config_file_path) > 0:
            pass
        else:
            raise Exception('{0}: Configuration does not exist.'.format(self.config_file_path))

        # List of configuration keys.
        config_keys = []

        for section in self.config.sections():
            # Added options from configuration file. Duplicates don't matter.
            config_keys.extend([opt.lower() for opt in self.config.options(section)])

        # Remove duplicate items from the list.
        config_keys = list(OrderedDict.fromkeys(config_keys))

        if config_keys == _params:
            # Check if all parameters exist in config_keys list.
            print("{0}: All parameters match.".format(self.config_file))
            pass
        elif set(_params).isdisjoint(config_keys):
            # Checks to make sure that some arguments exist.
            if len(_params) < len(config_keys):
                # If user provided fewer args than exist in the file, warn them.
                extra_args = ', '.join(list(set(config_keys) - set(_params)))
                print('{0}: Extra parameters found in file: {1}'.format(self.config_file,
                                                                        extra_args))
            else:
                # If user provided arguments not found in the config file, warn them.
                missing_args = ', '.join(list(set(_params) - set(config_keys)))
                print('{0}: Some parameters to check against missing in file: {1}'.format(self.config_file,
                                                                                          missing_args))
        else:
            raise Warning('No parameters passed exist in the config file.')

    def construct_dict(self, check_params: list = None) -> dict:
        """
        Turns configuration file into dict with mirrored structure. Structure will look like this:
        {section_name: {key_1: key_val, ...}, ...}

        There is an optional argument (list) that when passed will check if parameters exist in configuration
        file.

        The first loop goes through and finds each section. The inner loop takes each section and grabs each
        key from said respective section. NOTE: A section named [DEFAULT] will result in each section
        containing everything that was in the [DEFAULT] section.
        """

        if check_params:
            if type(check_params) is list:
                self._check_against_config(check_params)
            else:
                raise TypeError('Check_params should be a list, not {0}.'.format(type(check_params)))

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

        self.config_dict = config_dict
