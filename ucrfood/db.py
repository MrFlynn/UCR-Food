import rethinkdb as r
from datetime import datetime, timedelta


class Database:
    def __init__(self, port: int, uname: str, db_pass: str = None, host: str = None):
        """Initializes class variables and generates the connection to the database.

        :param host: IP of host to connect to database.
        :param port: Port on host where database is running.
        :param uname: Username with access to the database/table you are connecting to.
        :param db_pass: (optional) password used to access the database/table.
        """
        if not host:
            self.host = '127.0.0.1'
        else:
            self.host = host

        self.port = port
        self.db_username = uname
        self.db_password = db_pass
        self.database = 'ucrfood'

        # List of unique indices that were created:
        self.indices = set()

        # Connections:
        self.conn = None
        self.__connect()

    def __connect(self):
        """Connects to RethinkDB server. If no database password is provided, then connect without
        authentication.
        """

        if not self.db_password:
            self.conn = r.connect(self.host,
                                  self.port,
                                  self.database,
                                  self.db_username)
        else:
            self.conn = r.connect(self.host,
                                  self.port,
                                  self.database,
                                  self.db_username,
                                  self.db_password)

    def __generate_index(self, index_name: str) -> bool:
        """Creates an index with a given index to represent the menu_date nested index.

        todo: make this work for creating any index.

        :param index_name: name for the secondary index to generate.
        :return: whether or not the operation completed successfully.
        """
        try:
            # If the index doesn't exist, create it.
            if index_name not in r.table('menus').index_list().run(self.conn):
                r.table('menus')\
                    .index_create(index_name, r.row['time_info']['menu_date'])\
                    .run(self.conn)

            # Check to see if the index is ready. If it is, add to indices set and return true.
            if r.table('menus').index_wait(index_name).run(self.conn)[0].get('ready'):
                self.indices.add(index_name)
                return True
            else:
                return False
        except r.errors.ReqlOpFailedError as e:
            # If some sort of operation failed, print the error to the console and return false.
            print(e)
            return False

    def add_menu_data(self, menu: dict):
        """Method for inserting menu into 'menus' table.

        :param menu: menu to insert into the table.
        """

        r.table('menus').insert(menu).run(self.conn)

    def update_menu_on_date(self, date: str, menu: dict):
        """Replace menu for specific date in 'menus' table.

        :param date: date to replace menu entry on.
        :param menu: menu to replace with.
        """
        if not self.__generate_index('time_date'):
            pass

        r.table('menus').filter({'time_date': date}).replace(menu).run(self.conn)

    def get_page_info_within_range(self, day_delta: int) -> list:
        """Returns all table entries from the current date to n days from now.

        :param day_delta: number of days from the current date to pull.
        :return: Returns list of menu entries between two dates.
        """

        # Create the start and end dates based on the current date and given timedelta.
        start_date = str(datetime.now().date())
        end_date = str(datetime.now().date() + timedelta(days=day_delta))

        # If the index was not successfully generated, return an empty list.
        if not self.__generate_index('time_date'):
            return list()

        # Return list containing dicts with urls and page md5sums.
        return list(r.table('menus')
                    .between(start_date, end_date, index='time_date')
                    .pluck(['sum', 'url']).run(self.conn)
                    )

    def disconnect(self):
        """Drops all indices that were created and closes the connection to the database.
        """
        # Drop all indices before disconnecting.
        for i in list(self.indices):
            r.table('menus').index_drop(i).run(self.conn)

        self.conn.close()