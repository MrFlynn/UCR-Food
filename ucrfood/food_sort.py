import requests.exceptions as rexcept
from requests import get
from urllib.parse import urlparse, parse_qs, quote
from bs4 import BeautifulSoup
from typing import TypeVar, Generic
from datetime import datetime
from hashlib import md5
from re import sub, compile
from multiprocessing import Process, Manager


class FoodSort:
    url_types = TypeVar('url_types', str, dict, list)

    def __init__(self, urls: Generic[url_types]):
        # Special list that is accessible between threads.
        self.__serialized_menus = Manager().list()

        if isinstance(urls, str):
            self.__urls = [{'url': urls, 'sum': None, 'content': None}]
        elif isinstance(urls, dict):
            self.__urls = [urls.update({'content': None})]
        elif isinstance(urls, list):
            if all(isinstance(i, dict) for i in urls):
                self.__urls = urls
            else:
                self.__urls = [{'url': i, 'content': None} for i in urls]
        else:
            raise TypeError('Url is not an instance or list or str.')

    @staticmethod
    def __pull_page(url: str) -> str:
        """Gets the page from the given url and returns the page content.

        :param url: url to get page content from.
        :return: page content.
        """
        try:
            return get(url).content
        except rexcept.ConnectionError:
            return str()

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
        try:
            return parse_qs(urlparse(url).query).get(parameter)[index]
        except IndexError:
            return str()

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

        # Cast the Manager list to native Python list.
        return list(self.__serialized_menus)

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
        serial['sum'] = self.__get_page_sum(url_entry.get('content'))

        return serial

    def __serialize_menu(self, url_entry: dict) -> list:
        """Parses the the menu web page for menu items and returns them in list form.

        :param url_entry: dict containing the page content.
        :return: list of menu items for each dining time (i.e. breakfast, lunch, & dinner).
        """

        # Generate the page tree and find all sections containing items on the menu.
        html_tree = BeautifulSoup(url_entry.get('content'), 'lxml')
        menu_entries = html_tree.find_all('td', attrs={'width': ['50%', '30%']})

        # Breakfast, lunch, and dinner menus.
        menus = []

        for entry in menu_entries:
            # Subsections from each menu time with menu entries and the working section.
            menu_sections = dict()
            current_section = None

            # Get text only from all elements within the page tree.
            sec_items = [el.get_text() for el in entry.find_all(compile('a[name="Recipe_Desc"]'))]

            for item in sec_items:
                if item[:2] == '--':
                    # If the item starts with '--' in the name, this is the working section.
                    section_name = item[3:-3]

                    # Set working section and update menu_sections dictionary.
                    current_section = section_name
                    menu_sections.update({section_name: []})
                else:
                    # Remove extraneous characters from menu item.
                    menu_item = self.__strip_characters(item)

                    # Append to list if not an empty string.
                    if menu_item:
                        menu_sections.get(current_section).append(menu_item)

            # Append all the menu sections to the menu.
            menus.append({'type': entry.find('div', class_='shortmenumeals').get_text(),
                          'content': menu_sections})

        return menus

    def __get_menu(self, url_entry: dict):
        """Checks if the supplied md5sum is the same as the one for the page being processed. If it
        is, skip parsing.

        :param url_entry: dict containing url, page content, and page sum.
        :return: list containing menu items from each dining section.
        """

        # Sets the content of the page in the url_entry dict.
        url_entry['content'] = self.__pull_page(url_entry.get('url'))

        # Create the dictionary using the __create_single_menu_serial method.
        menu_dict = self.__create_single_menu_serial(url_entry)

        # If the entry's md5sum is not the same then serialize the page.
        if menu_dict['sum'] != url_entry.get('sum') or url_entry.get('sum') is None:
            menu_dict['menus'] = self.__serialize_menu(url_entry)

            # Append to the manager list.
            self.__serialized_menus.append(menu_dict)

    def get_menus(self):
        """Processes list of urls using as many threads as possible.

        :return: N/A
        """
        # List of processes to run.
        processes = []

        # Append processes to process list.
        for u in self.__urls:
            p = Process(target=self.__get_menu, args=(u, ))
            processes.append(p)

        # Start and then kill the processes.
        for p in processes:
            p.start()
        for p in processes:
            p.join()
