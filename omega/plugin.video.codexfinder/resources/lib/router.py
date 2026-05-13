import urllib.parse
import xbmcgui
import xbmcplugin
import xbmc 
import json 

from .utils import HANDLE, BASE_URL, ICON, ADDON
from .xml_loader import load_movies
from .movie_view import display_movies

def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)

def show_main_menu():
    # ১. ডিফল্ট মেনু আইটেম
    menu_items = [
        ("[B][COLOR cyan]Search[/COLOR][/B]", 'search'),
        ("[B][COLOR cyan]Movies By Year[/COLOR][/B]", 'years'),
        ("[B][COLOR cyan]All Movies (Main)[/COLOR][/B]", 'all_movies')
    ]

    for label, action in menu_items:
        item = xbmcgui.ListItem(label)
        item.setArt({'icon': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action=action), item, True)

    # ২. কাস্টম অ্যাড করা XML ফাইলগুলো যোগ করা
    custom_data = ADDON.getSetting('xml_list')
    if custom_data:
        try:
            xml_list = json.loads(custom_data)
            for entry in xml_list:
                item = xbmcgui.ListItem(f"[B][COLOR gold]{entry['name']}[/COLOR][/B]")
                item.setArt({'icon': ICON})
                url = get_url(action='custom_view', custom_path=entry['path'])
                xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
        except:
            pass

    xbmcplugin.endOfDirectory(HANDLE)

# এরর সমাধান: add_xml_file ফাংশনটি এখানে ডিফাইন করা থাকতে হবে
def add_xml_file():
    name = xbmcgui.Dialog().input('Enter Directory Name (e.g. My Collection)')
    if not name: return

    options = ['Add via URL (Link)', 'Select Local XML File']
    choice = xbmcgui.Dialog().select('Choose Source Type', options)

    path = None
    if choice == 0:
        path = xbmcgui.Dialog().input('Enter XML URL:')
    elif choice == 1:
        path = xbmcgui.Dialog().browse(1, 'Select Local Movie XML File', 'files', '.xml')

    if path:
        current_data = ADDON.getSetting('xml_list')
        try:
            xml_list = json.loads(current_data) if current_data else []
        except:
            xml_list = []

        xml_list.append({'name': name, 'path': path})
        ADDON.setSetting('xml_list', json.dumps(xml_list))
        xbmcgui.Dialog().notification('Success', f'"{name}" Added!', ICON, 3000)
        xbmc.executebuiltin('Container.Refresh')

def delete_xml_file():
    if xbmcgui.Dialog().yesno('Confirm Delete', 'Delete ALL custom added directories?'):
        ADDON.setSetting('xml_list', '[]')
        xbmcgui.Dialog().notification('Deleted', 'All paths cleared!', ICON, 3000)
        xbmc.executebuiltin('Container.Refresh')

def show_years():
    # মেইন মুভি থেকে বছর ফিল্টার করা
    movies = load_movies(mode="main_all")
    years = sorted(set(str(m['year']) for m in movies if m.get('year')), reverse=True)

    for year in years:
        item = xbmcgui.ListItem(f"[B][COLOR lime]{year}[/COLOR][/B]")
        item.setArt({'icon': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action='movies_by_year', year=year), item, True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_all_movies(page=1, mode="main_all", custom_path=None):
    try:
        per_page = int(ADDON.getSetting('items_per_page'))
    except:
        per_page = 20

    movies = load_movies(mode=mode, custom_path=custom_path)
    
    if not movies:
        xbmcgui.Dialog().notification('Info', 'No movies found in this list', ICON, 2000)
        return

    start = (page - 1) * per_page
    end = start + per_page
    display_movies(movies[start:end])

    if end < len(movies):
        next_item = xbmcgui.ListItem("[B][COLOR gold]Next Page >>[/COLOR][/B]")
        action_type = 'all_movies' if mode == "main_all" else 'custom_view'
        url_params = {'action': action_type, 'page': page + 1}
        if custom_path: url_params['custom_path'] = custom_path
        xbmcplugin.addDirectoryItem(HANDLE, get_url(**url_params), next_item, True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')

    if action == 'search':
        # সার্চ লজিক এখানে হবে
        pass
    elif action == 'years':
        show_years()
    elif action == 'all_movies':
        list_all_movies(page=int(params.get('page', 1)), mode="main_all")
    elif action == 'custom_view':
        list_all_movies(page=int(params.get('page', 1)), mode="custom_single", custom_path=params.get('custom_path'))
    elif action == 'add_xml':
        add_xml_file()
    elif action == 'delete_xml':
        delete_xml_file()
    else:
        show_main_menu()