# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import xbmcgui


def fetch_xml_data(xml_url):

    try:
        headers = {'User-Agent': 'Kodi/1.0'}

        req = urllib.request.Request(xml_url, headers=headers)

        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        return root

    except urllib.error.URLError as e:

        xbmcgui.Dialog().notification(
            "Movie Club",
            f"URL Error: {str(e)}",
            xbmcgui.NOTIFICATION_ERROR
        )

        return None

    except ET.ParseError as e:

        xbmcgui.Dialog().notification(
            "Movie Club",
            f"Parse Error: {str(e)}",
            xbmcgui.NOTIFICATION_ERROR
        )

        return None

    except Exception as e:

        xbmcgui.Dialog().notification(
            "Movie Club",
            f"Error: {str(e)}",
            xbmcgui.NOTIFICATION_ERROR
        )

        return None