#!/usr/bin/env python3

from ucrfood import food_sort
import json


def main():
    m = food_sort.FoodSort('http://138.23.12.141/foodpro/shortmenu.asp?locationNum=03&locationName=A+%2D+I+Residential+Restaurant&dtdate=11%2F3%2F2017')
    m.get_menus()
    print(json.dumps(m.menus))


if __name__ == '__main__':
    main()
