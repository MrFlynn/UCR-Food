#!/usr/bin/env python3

import ucrfood
import sys
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from multiprocessing import Pool

"""
Set the recursion limit to prevent errors with multi threading.
"""
sys.setrecursionlimit(100000)


"""
Global variables for main function:
"""

# Sets database variable to null.
app_db = None

# Bases for urls to use during runtime.
base_urls = []


def _construct():
    """
    Description: runs when application is first starts up. Opens configuration
    files, constructs the list of urls from which to pull data, and then
    build the database connection.
    """

    # Location configuration
    location_config = ucrfood.Config('location.ini')
    location_config.construct_dict(check_params=['BaseURL',
                                                 'LocationNum',
                                                 'LocationName'])

    # Rethink configuration
    db_config = ucrfood.Config('db.ini')
    db_config.construct_dict(check_params=['DBName',
                                           'DBUsername',
                                           'Host',
                                           'Port',
                                           'DBPassword'])

    # Construct base urls
    for key in location_config.config_dict:
        if key == 'MAIN':
            continue
        else:
            join_str = '&'
            base_url = location_config.config_dict.get('MAIN').get('baseurl')
            url_args = []

            for inner_keys in location_config.config_dict.get(key).items():
                arg_join_str = '='
                url_args.append(arg_join_str.join(inner_keys))

            full_url = '{base}?{args}'.format(base=base_url,
                                              args=join_str.join(url_args))

            base_urls.append(full_url)

    # RethinkDB connection details:
    db_init_args = (db_config.config_dict.get('CONNECTION').get('host'),
                    db_config.config_dict.get('CONNECTION').get('port'),
                    db_config.config_dict.get('DB_INFO').get('dbname'),
                    db_config.config_dict.get('DB_INFO').get('dbusername'),
                    db_config.config_dict.get('AUTH').get('dbpassword'))

    # Initialize database connection:
    app_db = ucrfood.Database(*db_init_args)


def main():
    """
    Builds all urls with date parameters, grabs data from the site, and
    then uploads all data to the database.
    """

    # Urls with date objects:
    runtime_urls = []

    # Get menus for the next two weeks and push to database:
    for url in base_urls:
        for i in range(15):
            # Get run date + timedelta:
            current_date = quote_plus((datetime.now().date() +
                                      timedelta(days=i)).strftime('%m/%d/%Y'))

            # Construct the url with the new date:
            current_url = '{base}&dtdate={date}'.format(base=url,
                                                        date=current_date)

            runtime_urls.append(current_url)

    with Pool(processes=4) as pool:
        # Grab and sort the data from each url:
        results = [pool.apply_async(ucrfood.FoodSort, (i, )) for i in runtime_urls]

        # Push to the database:
        for item in results:
            app_db.add_menu_data(item.get().tree_data)

# Run the application:
if __name__ == '__main__':
    # todo: have main function run within a scheduler.

    _construct()
    main()
