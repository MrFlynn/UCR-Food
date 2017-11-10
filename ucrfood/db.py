import rethinkdb as rdb
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
        self.table = 'ucrfood'

        # Connection
        self.conn = None
        self.__connect()

    def __connect(self):
        """Connects to RethinkDB server. If no database password is provided, then connect without
        authentication.
        """

        if not self.db_password:
            self.conn = rdb.connect(self.host,
                                    self.port,
                                    self.table,
                                    self.db_username)
        else:
            self.conn = rdb.connect(self.host,
                                    self.port,
                                    self.table,
                                    self.db_username,
                                    self.db_password)

    def add_menu_data(self, menu: dict):
        """Method for inserting menu into 'menus' table.

        :param menu: menu to insert into the table.
        """

        rdb.table('menus').insert(menu).run(self.conn)

    def update_menu_on_date(self, date: str, menu: str):
        """Replace menu for specific date in 'menus' table.

        :param date: date to replace menu entry on.
        :param menu: menu to replace with.
        """

        rdb.table('menus').filter({'menu_date': date}).replace(menu).run(self.conn)

    def get_menu_with_duration(self, day_delta: int):
        """Returns all table entries from the current date to n days from now.

        :param day_delta: number of days from the current date to pull.
        :return: Returns list of menu entries between two dates.
        """

        start_date = str(datetime.now().date())
        end_date = str(datetime.now().date() + timedelta(days=day_delta))

        return rdb.table('menus').between({'menu_date': start_date},
                                          {'menu_date': end_date}).run(self.conn)
