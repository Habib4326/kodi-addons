# -*- coding: utf-8 -*-
import sys
import urllib.parse
import urllib.request
import os
import xbmcgui
import xbmcplugin
import xbmcaddon
import xml.etree.ElementTree as ET

# অ্যাডঅন কনস্ট্যান্ট
ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
ADDON_PATH = ADDON.getAddonInfo('path')

# GitHub XML URL
XML_URL = "https://raw.githubusercontent.com/Habib4326/ICC_Live_posterxml/main/movie_database.xml"

ICON = os.path.join(ADDON_PATH, "icon.png")
FANART_DEFAULT = os.path.join(ADDON_PATH, "fanart.jpg")


def get_url(**kwargs):
    """প্লাগইন URL তৈরি করার সহায়ক ফাংশন"""
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)


def show_main_menu():
    """সার্চ এবং অল মুভিজ মেনু"""
    
    search_url = get_url(action='search')
    list_item = xbmcgui.ListItem(label='🔍 Search Movie')
    list_item.setArt({'icon': ICON, 'thumb': ICON, 'fanart': FANART_DEFAULT})
    xbmcplugin.addDirectoryItem(HANDLE, search_url, list_item, True)

    all_url = get_url(action='list_all')
    list_item = xbmcgui.ListItem(label='📂 All Movies')
    list_item.setArt({'icon': ICON, 'thumb': ICON, 'fanart': FANART_DEFAULT})
    xbmcplugin.addDirectoryItem(HANDLE, all_url, list_item, True)

    xbmcplugin.endOfDirectory(HANDLE)


def run_search():
    """কোডি কিবোর্ড ওপেন করে সার্চ"""
    
    kb = xbmcgui.Dialog().input('Search Movie', type=xbmcgui.INPUT_ALPHANUM)

    if kb:
        display_movies(query=kb.lower())
    else:
        show_main_menu()


def load_movies():
    """GitHub URL থেকে সরাসরি XML লোড করা (লোকাল ফাইল সেভ হবে না)"""
    movies = []

    try:
        # URL থেকে ডেটা পড়া
        response = urllib.request.urlopen(XML_URL)
        xml_data = response.read()
        
        # স্ট্রিং থেকে XML পার্স করা
        root = ET.fromstring(xml_data)

        for movie in root.findall("movie"):
            movies.append({
                "title": movie.findtext("title", "Unknown"),
                "link": movie.findtext("link", ""),
                "poster": movie.findtext("poster", ""),
                "rating": movie.findtext("rating", "N/A")
            })

    except Exception as e:
        xbmcgui.Dialog().ok("Error", "Online XML load failed: " + str(e))

    return movies


def display_movies(query=None):
    """মুভি তালিকা প্রদর্শন করা"""

    movies = load_movies()

    if query:
        results = [m for m in movies if query in m['title'].lower()]
    else:
        results = movies

    if not results:
        xbmcgui.Dialog().notification('No Results', 'No matching movies found.', xbmcgui.NOTIFICATION_INFO, 3000)
        return

    for movie in results:
        list_item = xbmcgui.ListItem(label=movie['title'])

        movie_poster = movie.get('poster') if movie.get('poster') else ICON
        movie_fanart = movie.get('poster') if movie.get('poster') else FANART_DEFAULT

        list_item.setArt({
            'icon': ICON,
            'thumb': movie_poster,
            'poster': movie_poster,
            'fanart': movie_fanart
        })

        plot_text = u"⭐ Rating: {}\n🔗 Source: GitHub Online".format(movie.get('rating', 'N/A'))

        list_item.setInfo('video', {
            'title': movie['title'],
            'plot': plot_text,
            'mediatype': 'movie'
        })

        list_item.setProperty('IsPlayable', 'true')
        url = movie['link']

        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=url,
            listitem=list_item,
            isFolder=False
        )

    xbmcplugin.endOfDirectory(HANDLE)


def router(paramstring):
    """রাউটিং"""
    params = dict(urllib.parse.parse_qsl(paramstring))

    if params:
        if params['action'] == 'search':
            run_search()
        elif params['action'] == 'list_all':
            display_movies()
    else:
        show_main_menu()


if __name__ == '__main__':
    router(sys.argv[2][1:])