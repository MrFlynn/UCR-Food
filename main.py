# Imports:
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from lxml import html
import requests
import re


class FoodSort(object):
    """
    Description: grabs dining hall menu web page and restructures it to an object format.
    Methods:
    - daily_menu_tree : grabs the web page, generated the tree, and returns the menu sections.
    - sort_data : parses the tree and returns an object sorted by menu_section -> dining hall food section -> menu item.
    """
    def __init__(self, url):
        self.url = url
        self.daily_menu = None
        self.tree_data = {}

        # Generates header info for daily_menu object:
        self.gen_header()
        # Generate daily menu html_tree.
        self.daily_menu_tree()
        # Generate json output.
        self.sort_data()

    def gen_header(self):
        """
        Adds generated time, location name, and update time to tree_data object.
        """
        self.tree_data['generated_time'] = str(datetime.now())
        self.tree_data['location_name'] = parse_qs(urlparse(self.url).query).get('locationName')[0]
        self.tree_data['update_time'] = None

    def daily_menu_tree(self):
        """
        Grabs webpage and returns the tree.
        """
        page = requests.get(self.url)
        html_tree = html.fromstring(page.content)
        self.daily_menu = html_tree.findall('.//td[@width="30%"]')

    def sort_data(self):
        for dining_section in self.daily_menu:
            # Resulting object-based data structure.
            result = {}
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
                                # Strip extraneous & most special characters:
                                ext_stripped = re.sub('[^a-zA-Z0-9-() *.]', '', unsorted_menu_items[idx + count])
                                # Remove duplicate whitespaces:
                                sub_menu_items.append(re.sub(' +', ' ', ext_stripped))
                                # Delete item from master list.
                                del unsorted_menu_items[idx + count]
                                count += 1
                            else:
                                break
                        except IndexError:
                            # When the end of the list is reached, stop the while loop.
                            break

                    # Menu item to dining hall food section assignment.
                    result[item[3:-3]] = sub_menu_items

            # Set tree data to result.
            self.tree_data[dining_section.find_class("shortmenumeals")[0].text.lower()] = result
