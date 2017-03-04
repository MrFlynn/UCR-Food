# Imports:
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote
from lxml import html
import requests
import uuid
import re


class FoodSort(object):
    """
    Description: grabs dining hall menu web page and restructures it to an object format.
    Methods:
    - _daily_menu_tree : grabs the web page, generated the tree, and returns the menu sections.
    - sort_data : parses the tree and returns an object sorted by menu_section -> dining hall food section -> menu item.
    - _add_base_data : adds useful data to object and sets up structure of object.
    """
    def __init__(self, url: str, check_data: bool = True):
        # Initial class variables.
        self.url = url
        self.check_data = check_data  # Do you want data validity checks?
        self.daily_menu = None
        self.tree_data = {}

        # Check if function should be run. If it should, check validity of passed URL:
        if check_data:
            self._check_url_format()
        else:
            pass
        # Generates header info for daily_menu object:
        self._add_base_data()

    def _check_url_format(self):
        """
        Function checks to make sure url has correct query strings.
        """

        # List of url parameters to check.
        url_parameters = ['dtdate', 'locationNum', 'locationName']
        # Parse url for query strings.
        parsed_url = parse_qs(urlparse(self.url).query)

        # Check that all correct query strings are in passed url.
        for parameter in url_parameters:
            if parameter in parsed_url:
                continue
            else:
                raise Exception('URL does not contain proper query strings.')

    def _add_base_data(self) -> object:
        """
        Generates useful information for JSON object.
        - data : object containing parsed data from sort_data method.
        - location_data :
            - location_name : name of dining hall location.
            - location_num : dining hall location number.
        - generated_time : time the object was originally created.
        - update_time : in case menu changes and object needs to be updated.
        - source_url : encoded URL from which data was extracted.
        - menu_date : date for menu.
        """

        # Create data lists/objects:
        self.tree_data['data'] = []
        self.tree_data['location_data'] = {}

        # Add data as described above:
        self.tree_data['location_data']['location_name'] = parse_qs(urlparse(self.url).query).get('locationName')[0]
        self.tree_data['location_data']['location_num'] = parse_qs(urlparse(self.url).query).get('locationNum')[0]
        self.tree_data['generated_time'] = str(datetime.now())
        self.tree_data['update_time'] = None
        self.tree_data['uuid'] = str(uuid.uuid4())
        self.tree_data['source_url'] = quote(self.url, safe='')
        self.tree_data['menu_date'] = parse_qs(urlparse(self.url).query).get('dtdate')[0].replace('/', '-')

    def _daily_menu_tree(self) -> object:
        # Grabs web page and returns the tree.

        page = requests.get(self.url)
        html_tree = html.fromstring(page.content)
        self.daily_menu = html_tree.findall('.//td[@width="30%"]')

    def sort_data(self) -> dict:
        # Grab page and generate tree.
        self._daily_menu_tree()

        for dining_section in self.daily_menu:
            # Resulting object-based data structure.
            food_dict = {}
            # Filters html tree for unsorted dining hall food sections/menu items.
            unsorted_menu_items = dining_section.xpath('.//a[@name="Recipe_Desc"]/text()|\
                                                        .//div[@class="shortmenucats"]/span/text()')

            """
            Main loop:
            Filters menu items from dining hall food sections. Assigns menu items to respective
            dining hall food sections.
            """
            for idx, item in enumerate(unsorted_menu_items):
                if item[:2] == '--':
                    sub_menu_items = []

                    while True:
                        count = 1

                        try:
                            if unsorted_menu_items[idx + count][:2] != '--':
                                # Remove duplicate whitespaces & strip extraneous & most special characters:
                                sub_menu_items.append(re.sub(' +',
                                                             ' ',
                                                             re.sub('[^a-zA-Z0-9-() *.]',
                                                                    '',
                                                                    unsorted_menu_items[idx + count])))
                                # Delete item from master list.
                                del unsorted_menu_items[idx + count]
                                count += 1
                            else:
                                break
                        except IndexError:
                            # When the end of the list is reached, stop the while loop.
                            break

                    # Menu item to dining hall food section assignment.
                    food_dict[item[3:-3]] = sub_menu_items

            # Set tree data to food_dict.
            self.tree_data['data'].append({'type': dining_section.find_class("shortmenumeals")[0].text.lower(),
                                           'content': food_dict})
