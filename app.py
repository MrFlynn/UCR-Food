#!/usr/bin/env python

import os
from FoodService import FoodService

# Application entrypoint:
if __name__ == '__main__':
    app = FoodService(url_conf=os.path.abspath('./config/location.ini'),
                      db_conf=os.path.abspath('./config/db.ini'))

    # Run the application.
    app.run()