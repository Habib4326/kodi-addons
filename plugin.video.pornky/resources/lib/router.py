# -*- coding: utf-8 -*-

import urllib.parse
import xbmcgui

from resources.lib.menu import build_menu
from resources.lib.item_listing import list_items


def router(paramstring):

    params = dict(urllib.parse.parse_qsl(paramstring))

    action = params.get('action')

    if action == 'list_items':

        category_url = params.get('category_url')

        if category_url:
            list_items(category_url)

        else:
            xbmcgui.Dialog().notification(
                "Movie Club",
                "Category URL Missing",
                xbmcgui.NOTIFICATION_ERROR
            )

    else:
        build_menu()