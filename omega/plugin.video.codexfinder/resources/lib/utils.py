# resources/lib/utils.py

import xbmcaddon
import os

ADDON = xbmcaddon.Addon()

ADDON_PATH = ADDON.getAddonInfo('path')

ICON = os.path.join(
    ADDON_PATH,
    'resources/media/icon.png'
)

FANART = os.path.join(
    ADDON_PATH,
    'resources/media/fanart.jpg'
)

HANDLE = int(__import__('sys').argv[1])
BASE_URL = __import__('sys').argv[0]


def safe(text):
    try:
        return text.encode('utf-8', 'ignore').decode('utf-8')
    except:
        return str(text)