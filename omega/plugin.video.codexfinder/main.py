# -*- coding: utf-8 -*-
import sys
import urllib.parse
import urllib.request
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xml.etree.ElementTree as ET

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# আগে ভুল ছিল (xml_url use করছিলে path হিসেবে)
# এটা ঠিক
ADDON_PATH = ADDON.getAddonInfo('path')

# Dynamic XML URL (settings থেকে)
XML_URL = ADDON.getSetting('xml_url') or "https://raw.githubusercontent.com/Habib4326/ICC_Live_posterxml/main/movie_database.xml"

ICON = os.path.join(ADDON_PATH, "icon.png")
FANART_DEFAULT = os.path.join(ADDON_PATH, "fanart.jpg")

MOVIE_CACHE = None


# ---------------- SAFE TEXT ----------------
def safe(text):
    try:
        return text.encode('utf-8', 'ignore').decode('utf-8')
    except:
        return str(text)


# ---------------- URL BUILDER ----------------
def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)


# ---------------- LOAD XML ----------------
def load_movies():
    global MOVIE_CACHE

    if MOVIE_CACHE:
        return MOVIE_CACHE

    movie_list = []
    try:
        response = urllib.request.urlopen(XML_URL)
        xml_data = response.read()
        root = ET.fromstring(xml_data)

        for movie in root.findall("movie"):
            movie_list.append({
                "title": safe(movie.findtext("title", "Unknown")),
                "year": str(movie.findtext("year", "0")).strip(),
                "link": movie.findtext("link", ""),
                "poster": movie.findtext("poster", ""),
                "rating": movie.findtext("rating", "N/A")
            })

    except Exception as e:
        xbmc.log("XML Load Error: " + str(e), xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Error", str(e))

    MOVIE_CACHE = movie_list
    return movie_list


# ---------------- MAIN MENU ----------------
def show_main_menu():

    # Search
    item1 = xbmcgui.ListItem("Search")
    item1.setArt({'icon': ICON, 'thumb': ICON})
    xbmcplugin.addDirectoryItem(HANDLE, get_url(action='search'), item1, True)

    # Movies
    item2 = xbmcgui.ListItem("Movies")
    item2.setArt({'icon': ICON, 'thumb': ICON})
    xbmcplugin.addDirectoryItem(HANDLE, get_url(action='years'), item2, True)

    # All Movies
    item3 = xbmcgui.ListItem("All Movies")
    item3.setArt({'icon': ICON, 'thumb': ICON})
    xbmcplugin.addDirectoryItem(HANDLE, get_url(action='all_movies'), item3, True)

    xbmcplugin.endOfDirectory(HANDLE)


# ---------------- YEARS ----------------
def show_years():
    movies = load_movies()
    years = sorted(set(str(m['year']) for m in movies), reverse=True)

    for year in years:
        item = xbmcgui.ListItem(safe(year))
        item.setArt({'icon': ICON, 'thumb': ICON})

        xbmcplugin.addDirectoryItem(
            HANDLE,
            get_url(action='movies_by_year', year=year),
            item,
            True
        )

    xbmcplugin.endOfDirectory(HANDLE)


# ---------------- MOVIES BY YEAR ----------------
def list_movies_by_year(year):
    movies = load_movies()
    filtered = [m for m in movies if str(m['year']) == str(year)]

    if not filtered:
        xbmcgui.Dialog().ok("Info", "No movies found for year " + str(year))
        return

    display_movies(filtered)
    xbmcplugin.endOfDirectory(HANDLE)


# ---------------- ALL MOVIES ----------------
def list_all_movies(page=1):

    # settings থেকে per page
    try:
        per_page = int(ADDON.getSetting('items_per_page'))
    except:
        per_page = 20

    movies = load_movies()
    movies = sorted(movies, key=lambda x: x['title'])

    start = (page - 1) * per_page
    end = start + per_page

    display_movies(movies[start:end])

    if end < len(movies):
        next_item = xbmcgui.ListItem("Next Page >>")
        next_item.setArt({'icon': ICON, 'thumb': ICON})

        xbmcplugin.addDirectoryItem(
            HANDLE,
            get_url(action='all_movies', page=page + 1),
            next_item,
            True
        )

    xbmcplugin.endOfDirectory(HANDLE)


# ---------------- DISPLAY MOVIES ----------------
def display_movies(movies):
    for movie in movies:

        poster = movie['poster'] or ICON

        item = xbmcgui.ListItem(label=safe(movie['title']))

        item.setArt({
            'thumb': poster,
            'poster': poster,
            'fanart': poster
        })

        try:
            year_int = int(movie['year'])
        except:
            year_int = 0

        item.setInfo('video', {
            'title': movie['title'],
            'year': year_int,
            'rating': movie['rating'],
            'mediatype': 'movie'
        })

        item.setProperty('IsPlayable', 'true')

        xbmcplugin.addDirectoryItem(HANDLE, movie['link'], item, False)


# ---------------- SEARCH ----------------
def run_search():
    query = xbmcgui.Dialog().input('Search Movie')

    if not query:
        return

    movies = load_movies()
    results = [m for m in movies if query.lower() in m['title'].lower()]

    if not results:
        xbmcgui.Dialog().ok("Search", "No results found")
        return

    display_movies(results)
    xbmcplugin.endOfDirectory(HANDLE)


# ---------------- ROUTER ----------------
def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')

    if action == 'search':
        run_search()

    elif action == 'years':
        show_years()

    elif action == 'movies_by_year':
        list_movies_by_year(params.get('year'))

    elif action == 'all_movies':
        page = int(params.get('page', 1))
        list_all_movies(page)

    else:
        show_main_menu()


# ---------------- START ----------------
if __name__ == '__main__':
    router(sys.argv[2][1:])