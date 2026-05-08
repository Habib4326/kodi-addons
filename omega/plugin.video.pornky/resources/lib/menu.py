# -*- coding: utf-8 -*-

import sys
import urllib.parse
import xbmcplugin
import xbmcgui

from resources.lib.xml_loader import fetch_xml_data
from resources.lib.config import (
    MAIN_XML_URL,
    ADDON_ICON,
    ADDON_FANART
)

addon_handle = int(sys.argv[1])


# ----------------------------------------
# Safe XML Text Reader
# ----------------------------------------
def safe_text(element, tag, default=''):

    try:
        node = element.find(tag)

        if node is not None and node.text:
            return node.text.strip()

    except Exception:
        pass

    return default


# ----------------------------------------
# Build Main Menu
# ----------------------------------------
def build_menu():

    print("DEBUG: Building Main Menu")

    root_element = fetch_xml_data(MAIN_XML_URL)

    if root_element is None:

        xbmcgui.Dialog().notification(
            "Pornky Extra",
            "Failed to load Master XML",
            xbmcgui.NOTIFICATION_ERROR
        )

        xbmcplugin.endOfDirectory(
            addon_handle,
            succeeded=False
        )

        return

    # Find Categories
    categories = root_element.findall('category')

    if not categories:
        categories = root_element.findall('item')

    if not categories:

        xbmcgui.Dialog().notification(
            "Pornky Extra",
            "No Categories Found",
            xbmcgui.NOTIFICATION_WARNING
        )

        xbmcplugin.endOfDirectory(
            addon_handle,
            succeeded=False
        )

        return

    # ----------------------------------------
    # Loop Categories
    # ----------------------------------------
    for category_element in categories:

        # Safe Values
        category_name = safe_text(
            category_element,
            'title',
            'Unknown Category'
        )

        category_link_url = safe_text(
            category_element,
            'link'
        )

        # Skip Invalid Item
        if not category_link_url:

            print(
                f"WARNING: Missing link for category: {category_name}"
            )

            continue

        # Artwork
        thumb = safe_text(
            category_element,
            'thumb',
            ADDON_ICON
        )

        if not thumb:
            thumb = safe_text(
                category_element,
                'thumbnail',
                ADDON_ICON
            )

        fanart = safe_text(
            category_element,
            'fanart',
            ADDON_FANART
        )

        # Kodi List Item
        list_item = xbmcgui.ListItem(
            label=category_name
        )

        list_item.setArt({
            'thumb': thumb,
            'icon': thumb,
            'fanart': fanart
        })

        # Encode URL Safely
        encoded_url = urllib.parse.quote_plus(
            str(category_link_url)
        )

        # Plugin URL
        url = (
            sys.argv[0]
            + f'?action=list_items&category_url={encoded_url}'
        )

        # Add Directory Item
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=list_item,
            isFolder=True
        )

        print(
            f"DEBUG: Added Category -> {category_name}"
        )

    # End Directory
    xbmcplugin.endOfDirectory(addon_handle)

    print("DEBUG: Main Menu Loaded Successfully")