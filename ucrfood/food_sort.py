from typing import TypeVar, Generic
from datetime import datetime
from hashlib import md5

from urllib.parse import urlparse, parse_qs, quote
from requests import get

from bs4 import BeautifulSoup
from re import sub, compile

from multiprocessing import Pool, cpu_count


class FoodSort:
    url_types = TypeVar('url_types', str, dict, list)

    def __init__(self, urls: Generic[url_types], check_data: bool):
        self.__serialized_menus = []

        if isinstance(urls, str):
            self.__urls = [{'url': urls, 'sum': None, 'content': None}]
        elif isinstance(urls, dict):
            self.__urls = [urls.update({'content': None})]
        elif isinstance(urls, list):
            self.__urls = [i.update({'content': None}) for i in urls]
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
        serial['menus'] = None

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
        serial['sum'] = self.__get_page_sum(''.join(url_entry.get('content')))

        return serial

    def __serialize_menu(self, url_entry: dict) -> list:
        """Parses the the menu web page for menu items and returns them in list form.

        :param url_entry: dict containing the page content.
        :return: list of menu items for each dining time (i.e. breakfast, lunch, & dinner).
        """
        html_tree = BeautifulSoup(url_entry.get('content'), 'html.parser')
        menu_entries = html_tree.find_all('td', attrs={'width': '30%'})

        menus = []

        for entry in menu_entries:
            menu_dict = dict()
            menu_items = [el.get_text() for el in entry.find_all(compile('a[name="Recipe_Desc"]'))]

            for idx, item in enumerate(menu_items):
                if item[:2] == '--':
                    sub_menu_items = []

                    while True:
                        count = 1

                        try:
                            if not menu_items[idx + count]:
                                count += 1
                                continue
                            elif menu_items[idx + count][:2] != '--':
                                sub_menu_items.append(
                                    self.__strip_characters(menu_items[idx + count]))

                                del menu_items[idx + count]
                                count += 1
                            else:
                                break
                        except IndexError:
                            break

                    menu_dict[item[3:-3]] = sub_menu_items

            menus.append({'type': entry.find('div', class_='shortmenumeals').get_text(),
                         'content': menu_dict})

        return menus

    def __get_menu(self, url_entry: dict) -> dict:
        """Checks if the supplied md5sum is the same as the one for the page being processed. If it
        is, skip parsing.

        :param url_entry: dict containing url, page content, and page sum.
        :return: list containing menu items from each dining section.
        """

        # Sets the content of the page in the url_entry dict.
        url_entry['content'] = self.__pull_page(url_entry.get('url'))

        # Create the dictionary using the __create_single_menu_serial method.
        menu_dict = self.__create_single_menu_serial(url_entry)

        # If the entry's md5sum is not the same, then process the page.
        if menu_dict['sum'] != url_entry.get('sum'):
            menu_dict['menus'] = self.__serialize_menu(url_entry)
            return menu_dict

    def get_menus(self):
        """Processes list of urls using as many threads as possible.

        :return: N/A
        """
        with Pool(processes=cpu_count()) as pool:
            self.__serialized_menus = [pool.apply_async(self.__get_menu, i) for i in self.__urls]