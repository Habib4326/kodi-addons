# -*- coding: utf-8 -*-

import sys
import urllib.parse
import xbmcplugin
import xbmcgui

from resources.lib.xml_loader import fetch_xml_data
from resources.lib.config import (
    ADDON_ICON,
    ADDON_FANART
)

addon_handle = int(sys.argv[1])


# =========================================================
# Supported XML Tags
# =========================================================

CATEGORY_TAGS = [
    'category',
    'subcategory',
    'subcat',
    'folder',
    'group',
    'items'
]

VIDEO_TAGS = [
    'movie',
    'item',
    'video',
    'file',
    'channel',
    'stream',
    'link'
]


# =========================================================
# Safe XML Text Reader
# =========================================================

def safe_text(element, tag_names, default=''):

    if isinstance(tag_names, str):
        tag_names = [tag_names]

    for tag in tag_names:

        try:
            node = element.find(tag)

            if node is not None and node.text:
                return node.text.strip()

        except Exception:
            pass

    return default


# =========================================================
# Find Elements By Multiple Tags
# =========================================================

def find_elements(root, tag_list):

    found_items = []

    for tag in tag_list:
        found_items.extend(root.findall(tag))

    return found_items


# =========================================================
# Check If Element Has Child Categories
# =========================================================

def has_child_categories(element):

    for tag in CATEGORY_TAGS:

        children = element.findall(tag)

        if children:
            return True

    return False


# =========================================================
# Main List Function
# =========================================================

def list_items(current_xml_url):

    print(f"DEBUG: Loading XML -> {current_xml_url}")

    root_element = fetch_xml_data(current_xml_url)

    if root_element is None:

        xbmcgui.Dialog().notification(
            "Pornky Extra",
            "Failed To Load XML",
            xbmcgui.NOTIFICATION_ERROR
        )

        xbmcplugin.endOfDirectory(
            addon_handle,
            succeeded=False
        )

        return

    # =====================================================
    # Find Categories
    # =====================================================

    category_items = find_elements(
        root_element,
        CATEGORY_TAGS
    )

    # =====================================================
    # Find Video Items
    # =====================================================

    video_items = find_elements(
        root_element,
        VIDEO_TAGS
    )

    # =====================================================
    # Decide Mode
    # =====================================================

    is_category_mode = False

    items_to_show = []

    if category_items:

        items_to_show = category_items
        is_category_mode = True

    elif video_items:

        items_to_show = video_items

    # =====================================================
    # Empty Check
    # =====================================================

    if not items_to_show:

        xbmcgui.Dialog().notification(
            "Pornky Extra",
            "No Items Found",
            xbmcgui.NOTIFICATION_INFO
        )

        xbmcplugin.endOfDirectory(
            addon_handle,
            succeeded=False
        )

        return

    # =====================================================
    # Loop Items
    # =====================================================

    for element in items_to_show:

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = safe_text(
            element,
            ['title', 'name'],
            'Unknown'
        )

        # -------------------------------------------------
        # Link
        # -------------------------------------------------

        link = safe_text(
            element,
            ['link', 'url', 'src', 'path', 'file']
        )

        if not link:

            print(f"WARNING: Missing Link -> {title}")

            continue

        # -------------------------------------------------
        # Artwork
        # -------------------------------------------------

        thumb = safe_text(
            element,
            ['thumbnail', 'thumb', 'icon', 'image'],
            ADDON_ICON
        )

        fanart = safe_text(
            element,
            ['fanart', 'background', 'backdrop'],
            ADDON_FANART
        )

        poster = safe_text(
            element,
            ['poster'],
            thumb
        )

        banner = safe_text(
            element,
            ['banner'],
            poster
        )

        clearart = safe_text(
            element,
            ['clearart'],
            fanart
        )

        # -------------------------------------------------
        # Kodi List Item
        # -------------------------------------------------

        list_item = xbmcgui.ListItem(
            label=title
        )

        list_item.setArt({
            'thumb': thumb,
            'icon': thumb,
            'poster': poster,
            'banner': banner,
            'fanart': fanart,
            'clearart': clearart
        })

        # =================================================
        # CATEGORY MODE
        # =================================================

        if is_category_mode:

            encoded_url = urllib.parse.quote_plus(
                str(link)
            )

            url = (
                sys.argv[0]
                + f'?action=list_items&category_url={encoded_url}'
            )

            xbmcplugin.addDirectoryItem(
                handle=addon_handle,
                url=url,
                listitem=list_item,
                isFolder=True
            )

            print(f"DEBUG: Added Category -> {title}")

        # =================================================
        # VIDEO MODE
        # =================================================

        else:

            list_item.setProperty(
                'IsPlayable',
                'true'
            )

            # Metadata
            plot = safe_text(
                element,
                ['plot', 'description', 'summary']
            )

            genre = safe_text(
                element,
                ['genre', 'category']
            )

            year = safe_text(
                element,
                ['year', 'date']
            )

            try:
                year = int(year)
            except:
                year = 0

            list_item.setInfo('video', {
                'title': title,
                'plot': plot,
                'genre': genre,
                'year': year
            })

            xbmcplugin.addDirectoryItem(
                handle=addon_handle,
                url=link,
                listitem=list_item,
                isFolder=False
            )

            print(f"DEBUG: Added Video -> {title}")

    # =====================================================
    # End Directory
    # =====================================================

    xbmcplugin.endOfDirectory(addon_handle)

    print("DEBUG: Directory Loaded Successfully")