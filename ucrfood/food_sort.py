from urllib.parse import urlparse, parse_qs, quote
from typing import TypeVar, Generic
from datetime import datetime
from requests import get
from hashlib import md5
from re import sub


class FoodSort:
    url_types = TypeVar('url_types', str, list)

    def __init__(self, urls: Generic[url_types], check_data: bool):
        self.__serialized_menus = []

        if isinstance(urls, str):
            self.__urls = [{'url': urls, 'content': None}]
        elif isinstance(urls, list):
            self.__urls = [{'url': i, 'content': None} for i in urls]
        else:
            raise TypeError('Url is not an instance or list or str.')

    @staticmethod
    def __pull_page(url: str) -> str:
        """Gets the page from the given url and returns the page content.

        :param url: url to get page content from.
        :return: page content.
        """

        return get(url).content

    @staticmethod
    def __get_page_sum(page_content: str) -> str:
        """Given a string containing the relevant page content, return the md5sum of said page.
        This is helpful for not parsing the page again when a copy exists in the database.

        :param page_content: string representing the page content.
        :return: md5sum of page_content.
        """
        m = md5()

        # Update the md5 parser with the content of the page and return the hex digest.
        m.update(page_content)
        return m.hexdigest()

    @staticmethod
    def __get_parameters(url: str, parameter: str, index: int) -> str:
        """Gets a specific parameter from the given url.

        :param url: url to parse.
        :param parameter: parameter to get from url.
        :param index: index in resulting list from getting parse_qs dict.
        :return: parameter set value.
        """
        return parse_qs(urlparse(url).query).get(parameter)[index]

    @staticmethod
    def __strip_characters(input_str: str) -> str:
        """Strips non alphanumeric characters and any duplicate whitespace.

        :param input_str: string to clean.
        :return: cleaned string.
        """
        filter_step = sub('[^a-zA-Z0-9-() *.]', '', input_str)
        return sub(' +', ' ', filter_step)

    @property
    def menus(self):
        """Returns list of dictionaries containing menu data.

        :return: list of dictionaries.
        """
        return self.__serialized_menus

    def __create_single_menu_serial(self, url_entry: dict) -> dict:
        """Creates base dictionary with menus, location date, time data, url, and page sum.

        :param url_entry: dict containing page url and content.
        :return: dictionary with data shown below.
        """
        # Declare dictionary.
        serial = dict()

        # Create empty list with menus.
        serial['menus'] = []

        # Create sub duct with location name and number.
        serial['location'] = {}
        serial['location']['name'] = self.__get_parameters(url_entry.get('url'), 'locationname', 0)
        serial['location']['num'] = self.__get_parameters(url_entry.get('url'), 'locationnum', 0)

        # Create sub dict with generation, update time and menu date.
        serial['time_info'] = {}
        serial['time_info']['gen'] = str(datetime.now())
        serial['time_info']['update'] = None
        serial['time_info']['menu_date'] = self.__get_parameters(url_entry.get('url'),
                                                                 'dtdate',
                                                                 0).replace('/', '-')

        # Source url and page sum.
        serial['url'] = quote(url_entry.get('url'), safe='')
        serial['sum'] = self.__get_page_sum(url_entry.get('content'))

        return serial
