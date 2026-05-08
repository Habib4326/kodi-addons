# resources/lib/movie_view.py

import xbmcgui
import xbmcplugin

from .utils import HANDLE, ICON, FANART, safe


def display_movies(movies):

    for movie in movies:

        poster = movie.get('poster') or ICON

        fanart = movie.get('fanart') or poster or FANART

        item = xbmcgui.ListItem(
            label=safe(movie['title'])
        )

        item.setArt({

            'icon': poster,

            'thumb': poster,

            'poster': poster,

            'fanart': fanart
        })

        item.setProperty(
            'fanart_image',
            fanart
        )

        try:
            year = int(movie.get('year', 0))
        except:
            year = 0

        item.setInfo('video', {

            'title': movie['title'],

            'year': year,

            'rating': movie.get('rating', 'N/A'),

            'mediatype': 'movie'
        })

        item.setProperty(
            'IsPlayable',
            'true'
        )

        xbmcplugin.addDirectoryItem(

            HANDLE,

            movie['link'],

            item,

            False
        )