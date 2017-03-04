#!/usr/bin/env python3

import ucrfood
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from multiprocessing import Pool


def main():
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

    # Generate and list URLS:
    base_urls = []

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

    # Rethink config details:
    db_init_args = (db_config.config_dict.get('CONNECTION').get('host'),
                    db_config.config_dict.get('CONNECTION').get('port'),
                    db_config.config_dict.get('DB_INFO').get('dbname'),
                    db_config.config_dict.get('DB_INFO').get('dbusername'),
                    db_config.config_dict.get('AUTH').get('dbpassword'))

    # Initialize database connection:
    rd_database = ucrfood.Database(*db_init_args)

    # List of base_urls with all the proper dates parametrized.
    complete_urls = []

    # Get menus for the next two weeks and push to database:
    for url in base_urls:
        for i in range(15):
            # Get run date + timedelta:
            current_date = (datetime.now().date()
                            + timedelta(days=i)).strftime('%m/%d/%Y')

            # Construct the url with the new date:
            current_url = '{base}&dtdate={date}'.format(base=url,
                                                        date=quote_plus(current_date))

            complete_urls.append(current_url)

    with Pool(processes=4) as pool:
        # Grab and sort the data from each url:

        results = [pool.apply_async(ucrfood.FoodSort, (i, )) for i in complete_urls]

        # Push to the database:
        for item in results:
            rd_database.add_menu_data(item.get().tree_data)

# Run the application:
if __name__ == '__main__':
    main()
