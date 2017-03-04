import rethinkdb as rdb
from datetime import datetime, timedelta


class Database(object):
    def __init__(self, host: str, port: int, db_name: str, db_username: str, db_password: str = None):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_username = db_username

        # Optional auth arguments
        self.db_password = db_password

        # Connection
        self.conn = None
        self._connect()

    def _connect(self):
        """
        Connects to RethinkDB server. If no database password is provided,
        then connect without authentication.
        """

        if not self.db_password:
            self.conn = rdb.connect(self.host,
                                    self.port,
                                    self.db_name,
                                    self.db_username)
        else:
            self.conn = rdb.connect(self.host,
                                    self.port,
                                    self.db_name,
                                    self.db_username,
                                    self.db_password)

    def add_menu_data(self, menu):
        """
        Method for inserting menu into 'menus' table.
        """

        rdb.table('menus').insert(menu).run(self.conn)

    def update_menu_on_date(self, date: str, menu: str):
        """
        Replace menu for specific date in 'menus' table.
        """

        rdb.table('menus').filter({'menu_date': date}).replace(menu).run(self.conn)

    def get_menu_with_duration(self, day_delta: int):
        """
        Returns all table entries from the current date to n days from now.
        """

        start_date = str(datetime.now().date())
        end_date = str(datetime.now().date() + timedelta(days=day_delta))

        return rdb.table('menus').between({'menu_date': start_date},
                                         {'menu_date': end_date}).run(self.conn)