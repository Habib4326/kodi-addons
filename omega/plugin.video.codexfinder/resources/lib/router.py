import urllib.parse
import xbmcgui
import xbmcplugin
import xbmc 

from .utils import HANDLE, BASE_URL, ICON, ADDON
from .xml_loader import load_movies, search_movies
from .movie_view import display_movies

def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)

def show_main_menu():
    menu_items = [
        ("[B][COLOR cyan]Search[/COLOR][/B]", 'search'),
        ("[B][COLOR cyan]Movies By Year[/COLOR][/B]", 'years'),
        ("[B][COLOR cyan]All Movies (Main)[/COLOR][/B]", 'all_movies')
    ]

    for label, action in menu_items:
        item = xbmcgui.ListItem(label)
        item.setArt({'icon': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action=action), item, True)

    xbmcplugin.endOfDirectory(HANDLE)

def show_years():
    movies = load_movies()
    
    if not movies:
        xbmcgui.Dialog().notification('Info', 'No movies found to filter years', ICON, 2000)
        xbmcplugin.endOfDirectory(HANDLE, False)
        return

    years = sorted(set(str(m['year']) for m in movies if m.get('year') and str(m['year']).isdigit()), reverse=True)

    for year in years:
        item = xbmcgui.ListItem(f"[B][COLOR lime]{year}[/COLOR][/B]")
        item.setArt({'icon': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action='movies_by_year', year=year), item, True)
        
    xbmcplugin.endOfDirectory(HANDLE)

def show_movies_by_year(year):
    movies = load_movies()
    filtered_movies = [m for m in movies if str(m.get('year')) == str(year)]
    
    if filtered_movies:
        display_movies(filtered_movies)
    else:
        xbmcgui.Dialog().notification('Info', f'No movies found for year {year}', ICON, 2000)
        
    xbmcplugin.endOfDirectory(HANDLE)

def list_all_movies(page=1):
    try:
        per_page = int(ADDON.getSetting('items_per_page'))
    except:
        per_page = 20

    movies = load_movies()
    
    if not movies:
        xbmcgui.Dialog().notification('Info', 'No movies found in this list', ICON, 2000)
        xbmcplugin.endOfDirectory(HANDLE, False)
        return

    start = (page - 1) * per_page
    end = start + per_page
    display_movies(movies[start:end])

    if end < len(movies):
        next_item = xbmcgui.ListItem("[B][COLOR gold]Next Page >>[/COLOR][/B]")
        url_params = {'action': 'all_movies', 'page': page + 1}
        xbmcplugin.addDirectoryItem(HANDLE, get_url(**url_params), next_item, True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')

    if action == 'search':
        # ১. কিবোর্ড ওপেন করার লজিক (যা আগে মিসিং ছিল)
        kb = xbmc.Keyboard('', 'Search Movies')
        kb.doModal()
        if kb.isConfirmed():
            search_query = kb.getText()
            if search_query:
                # xml_loader থেকে সার্চ ফাংশন দিয়ে মুভি খোঁজা
                results = search_movies(search_query)
                if results:
                    display_movies(results)
                else:
                    xbmcgui.Dialog().notification('No Results', 'No movies found!', ICON, 2000)
        xbmcplugin.endOfDirectory(HANDLE)
        
    elif action == 'years':
        show_years()
        
    elif action == 'movies_by_year':
        selected_year = params.get('year')
        show_movies_by_year(selected_year)
        
    elif action == 'all_movies':
        list_all_movies(page=int(params.get('page', 1)))
        
    else:
        show_main_menu()