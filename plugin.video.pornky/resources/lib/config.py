# -*- coding: utf-8 -*-

import xbmcaddon

addon = xbmcaddon.Addon()

try:
    MAIN_XML_URL = addon.getSettingString(
        'master_xml_url'
    )
except:
    MAIN_XML_URL = addon.getSetting(
        'master_xml_url'
    )

if not MAIN_XML_URL:

    MAIN_XML_URL = (
        "https://raw.githubusercontent.com/"
        "Habib4326/Kodi-Pornky/main/Main-Master.xml"
    )

ADDON_ICON = addon.getAddonInfo('icon')
ADDON_FANART = addon.getAddonInfo('fanart')