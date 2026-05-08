# resources/lib/xml_loader.py

import urllib.request
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui

from .utils import ADDON, safe

MOVIE_CACHE = None


def load_movies():

    global MOVIE_CACHE

    if MOVIE_CACHE:
        return MOVIE_CACHE

    # settings.xml setting id
    xml_url = ADDON.getSetting('xml_url')

    # fallback url
    if not xml_url:

        xml_url = (
            "https://raw.githubusercontent.com/"
            "Habib4326/ICC_Live_posterxml/main/"
            "movie_database.xml"
        )

    movie_list = []

    try:

        response = urllib.request.urlopen(xml_url)

        xml_data = response.read()

        root = ET.fromstring(xml_data)

        for movie in root.findall("movie"):

            movie_list.append({

                "title": safe(
                    movie.findtext(
                        "title",
                        "Unknown"
                    )
                ),

                "year": str(
                    movie.findtext(
                        "year",
                        "0"
                    )
                ).strip(),

                "link": movie.findtext(
                    "link",
                    ""
                ),

                "poster": movie.findtext(
                    "poster",
                    ""
                ),

                # NEW
                "fanart": movie.findtext(
                    "fanart",
                    ""
                ),

                "rating": movie.findtext(
                    "rating",
                    "N/A"
                )
            })

    except Exception as e:

        xbmc.log(
            "XML Load Error: " + str(e),
            xbmc.LOGERROR
        )

        xbmcgui.Dialog().ok(
            "Error",
            str(e)
        )

    MOVIE_CACHE = movie_list

    return movie_list