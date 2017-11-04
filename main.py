#!/usr/bin/env python3

import ucrfood
from datetime import datetime, timedelta
from urllib.parse import quote_plus


def _construct_base_urls():
    """
    Description: runs when application is first starts up. Opens 
    the location configuration file and constructs the list of 
    urls from which to pull data.
    """

    # Location configuration
    location_config = ucrfood.Config('location.ini')
    location_config.construct_dict(check_params=['BaseURL',
                                                 'LocationNum',
                                                 'LocationName'])

    # Bases for urls to use during runtime.
    base_urls = []

    # Construct base urls
    for key in location_config.config_dict:
        if key == 'MAIN':
            continue
        else:
            join_str = '&'
            base_url = location_config.get('MAIN').get('baseurl')
            url_args = []

            for inner_keys in location_config.get(key).items():
                arg_join_str = '='
                url_args.append(arg_join_str.join(inner_keys))

            full_url = '{base}?{args}'.format(base=base_url,
                                              args=join_str.join(url_args))

            base_urls.append(full_url)

    return base_urls


def _construct_database_conn():
    """
    Description: runs when application is first starts up. Opens 
    the database configuration file and then build the database connection. 
    """

    # Rethink configuration
    db_config = ucrfood.Config('db.ini')
    db_config.construct_dict(check_params=['DBName',
                                           'DBUsername',
                                           'Host',
                                           'Port',
                                           'DBPassword'])

    # RethinkDB connection details:
    db_init_args = (db_config.get('CONNECTION').get('host'),
                    db_config.get('CONNECTION').get('port'),
                    db_config.get('DB_INFO').get('dbname'),
                    db_config.get('DB_INFO').get('dbusername'),
                    db_config.get('AUTH').get('dbpassword'))

    # Initialize database connection:
    return ucrfood.Database(*db_init_args)


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

    f = ucrfood.FoodSort(runtime_urls)
    f.get_menus()
    for m in f.menus:
        app_db.add_menu_data(m)


# Run the application:
if __name__ == '__main__':
    # todo: have main function run within a scheduler.

    # Set the list of base urls as the result of the below function.
    base_urls = _construct_base_urls()

    # Set the database connection as the result of the below function.
    app_db = _construct_database_conn()

    # Main function.
    main()
