from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case

    start = ListItem()
    enter_name = ListItem()
    name_entered = ListItem()
    enter_password = ListItem()
    choose_filters = ListItem()
    filter_price = ListItem()
    filter_choose_category = ListItem()
    filter_search = ListItem()
    admin_panel = ListItem()
