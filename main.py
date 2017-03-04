#!/usr/bin/env python3

import ucrfood


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
                                           'Port,',
                                           'DBPassword'])

    # Generate and list URLS:
    urls = []

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

            urls.append(full_url)

    # Rethink config details:
    db_init_args = (db_config.config_dict.get('CONNECTION').get('host'),
                    db_config.config_dict.get('CONNECTION').get('port'),
                    db_config.config_dict.get('DB_INFO').get('dbname'),
                    db_config.config_dict.get('DB_INFO').get('dbusername'),
                    db_config.config_dict.get('AUTH').get('dbpassword'))

    # Initialize database connection:
    rd_database = ucrfood.Database(*db_init_args)

    # Get menu from current date and push to database:
    for loc in urls:
        current_menu = ucrfood.FoodSort(loc, False)
        current_menu.sort_data()
        rd_database.add_menu_data(current_menu.tree_data)

    # Print stuff out.
    print(rd_database.get_menu_with_duration(0))


# Run the application:
if __name__ == '__main__':
    main()
