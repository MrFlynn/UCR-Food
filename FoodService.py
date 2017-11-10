import ucrfood
from datetime import datetime, timedelta
from urllib.parse import quote_plus


class FoodService:
    def __init__(self, db_conf: str, url_conf: str):
        """Sets up the configuration parser for each ini file. Instantiates class specific vars.

        :param db_conf: path to database configuration file.
        :param url_conf: path to url configuration file.
        """
        self.__db_conf = ucrfood.Config(db_conf)
        self.__url_conf = ucrfood.Config(url_conf)

        self.base_urls = []
        self.__db_connection = None

    def __gen_base_urls(self):
        """Constructs the dictionary containing all of the url parameters and url base and then
        builds each base url.
        """
        self.__url_conf.construct_dict(check_params=['BaseURL', 'LocationNum', 'LocationName'])

        for key in self.__url_conf.config_dict:
            if key == 'MAIN':
                # Skip the main block.
                continue
            else:
                # Grab the base url and create url argument list.
                base_url = self.__url_conf.get('MAIN').get('baseurl')
                url_args = []

                for k in self.__url_conf.get(key).items():
                    # Join the key with its corresponding item.
                    url_args.append('='.join(k))

                full_url = '{base}?{args}'.format(base=base_url, args='&'.join(url_args))
                self.base_urls.append(full_url)

    def __gen_db_conn(self):
        """Constructs the dictionary containing all of the database settings and then initializes
        the connection.
        """
        self.__db_conf.construct_dict(check_params=['DBUsername',
                                                    'Host',
                                                    'Port',
                                                    'DBPassword'])

        self.__db_connection.ucrfood.Database(host=self.__db_conf.get('CONNECTION').get('host'),
                                              port=self.__db_conf.get('CONNECTION').get('port'),
                                              uname=self.__db_conf.get('DB_INFO').get('dbusername'),
                                              db_pass=self.__db_conf.get('AUTH').get('dbpassword'))

    def __gen_url_block(self):
        """Generates the complete list of URLs for the next 15 days and their corresponding date
        parameter.

        :return: list of urls.
        """
        block_urls = []

        # Iterate through each url and every day for the next 15 days.
        for u in self.base_urls:
            for d in range(15):
                # Use the current date and add the timedelta to get the correct date.
                current_date = (datetime.now().date() + timedelta(days=d)).strftime('%m/%d/%Y')

                # Construct the url using the base and the calculated date.
                current_url = '{base}&dtdate={date}'.format(base=u, date=quote_plus(current_date))
                block_urls.append(current_url)

        return block_urls

    def run(self):
        """Runs the application.
        """
        # Generate base urls and create database connection:
        self.__gen_base_urls()
        self.__gen_db_conn()

        # Instatiate menu processing code.
        menu_gen = ucrfood.FoodSort(self.__gen_url_block())

        # Serialize all menu pages and upload them to the database.
        menu_gen.get_menus()
        for m in menu_gen.menus:
            self.__db_connection.add_menu_data(m)
