# resources/lib/router.py

import urllib.parse
import xbmcgui
import xbmcplugin

from .utils import HANDLE, BASE_URL, ICON, ADDON
from .xml_loader import load_movies
from .movie_view import display_movies


def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)


def show_main_menu():

    item1 = xbmcgui.ListItem("Search")
    item1.setArt({'icon': ICON})

    xbmcplugin.addDirectoryItem(
        HANDLE,
        get_url(action='search'),
        item1,
        True
    )

    item2 = xbmcgui.ListItem("Movies")
    item2.setArt({'icon': ICON})

    xbmcplugin.addDirectoryItem(
        HANDLE,
        get_url(action='years'),
        item2,
        True
    )

    item3 = xbmcgui.ListItem("All Movies")
    item3.setArt({'icon': ICON})

    xbmcplugin.addDirectoryItem(
        HANDLE,
        get_url(action='all_movies'),
        item3,
        True
    )

    xbmcplugin.endOfDirectory(HANDLE)


def show_years():

    movies = load_movies()

    years = sorted(
        set(str(m['year']) for m in movies),
        reverse=True
    )

    for year in years:

        item = xbmcgui.ListItem(year)

        item.setArt({
            'icon': ICON,
            'thumb': ICON,
            'poster': ICON,
            'fanart': ICON
        })

        item.setProperty(
            'fanart_image',
            ICON
        )

        xbmcplugin.addDirectoryItem(
            HANDLE,
            get_url(
                action='movies_by_year',
                year=year
            ),
            item,
            True
        )

    xbmcplugin.endOfDirectory(HANDLE)


def list_movies_by_year(year):

    movies = load_movies()

    filtered = [
        m for m in movies
        if str(m['year']) == str(year)
    ]

    display_movies(filtered)

    xbmcplugin.endOfDirectory(HANDLE)


def list_all_movies(page=1):

    try:
        per_page = int(
            ADDON.getSetting(
                'items_per_page'
            )
        )

    except:
        per_page = 20

    movies = load_movies()

    start = (page - 1) * per_page

    end = start + per_page

    display_movies(
        movies[start:end]
    )

    if end < len(movies):

        next_item = xbmcgui.ListItem(
            "Next Page >>"
        )

        xbmcplugin.addDirectoryItem(
            HANDLE,
            get_url(
                action='all_movies',
                page=page + 1
            ),
            next_item,
            True
        )

    xbmcplugin.endOfDirectory(HANDLE)


def run_search():

    query = xbmcgui.Dialog().input(
        'Search Movie'
    )

    if not query:
        return

    movies = load_movies()

    results = [

        m for m in movies

        if query.lower()
        in m['title'].lower()
    ]

    display_movies(results)

    xbmcplugin.endOfDirectory(HANDLE)


def router(paramstring):

    params = dict(
        urllib.parse.parse_qsl(paramstring)
    )

    action = params.get('action')

    if action == 'search':

        run_search()

    elif action == 'years':

        show_years()

    elif action == 'movies_by_year':

        list_movies_by_year(
            params.get('year')
        )

    elif action == 'all_movies':

        page = int(
            params.get('page', 1)
        )

        list_all_movies(page)

    else:

        show_main_menu()