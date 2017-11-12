#!/usr/bin/env python

import os
from food_service import FoodService

# Application entrypoint:
if __name__ == '__main__':
    app = FoodService(url_conf=os.path.abspath('./config/location.ini'),
                      db_conf=os.path.abspath('./config/db.ini'))

    try:
        # Run every 24 hours.
        app.run_schedule(interval=24)
    except KeyboardInterrupt or SystemExit:
        print("\nStopping...")
        app.stop()
