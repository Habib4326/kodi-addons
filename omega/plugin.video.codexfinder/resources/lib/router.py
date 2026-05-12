import urllib.parse
import xbmcgui
import xbmcplugin
import xbmc 
import json # একাধিক ফাইল সেভ করার জন্য

from .utils import HANDLE, BASE_URL, ICON, ADDON
from .xml_loader import load_movies
from .movie_view import display_movies


def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)


def show_main_menu():
    # ১. ডিফল্ট মেনু আইটেমগুলো
    menu_items = [
        ("[B][COLOR cyan]Search[/COLOR][/B]", 'search'),
        ("[B][COLOR cyan]Movies By Year[/COLOR][/B]", 'years'),
        ("[B][COLOR cyan]All Movies (Main)[/COLOR][/B]", 'all_movies')
    ]

    for label, action in menu_items:
        item = xbmcgui.ListItem(label)
        item.setArt({'icon': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action=action), item, True)

    # ২. কাস্টম অ্যাড করা XML ডাইরেক্টরিগুলো যোগ করা
    custom_data = ADDON.getSetting('xml_list')
    if custom_data:
        try:
            xml_list = json.loads(custom_data)
            for entry in xml_list:
                # ইউজারের দেওয়া নামে নতুন ফোল্ডার তৈরি হবে
                item = xbmcgui.ListItem(f"[B][COLOR gold]{entry['name']}[/COLOR][/B]")
                item.setArt({'icon': ICON})
                # action হিসেবে 'custom_view' ব্যবহার করা হয়েছে
                url = get_url(action='custom_view', custom_path=entry['path'])
                xbmcplugin.addDirectoryItem(HANDLE, url, item, True)
        except:
            pass

    xbmcplugin.endOfDirectory(HANDLE)

# --- নতুন ফাংশন: নামসহ একাধিক XML ফাইল/URL অ্যাড করা ---
# --- নতুন ফাংশন: ফাইল ব্রাউজার এবং URL সাপোর্টসহ অ্যাড করা ---
def add_xml_file():
    # ১. প্রথমে ডিরেক্টরি নাম চাওয়া হবে
    name = xbmcgui.Dialog().input('Enter Directory Name (e.g. My Collection)')
    if not name: return

    # ২. ইউজারকে অপশন দেওয়া হবে সে কি URL দিবে নাকি ফাইল সিলেক্ট করবে
    options = ['Add via URL (Link)', 'Select Local XML File']
    choice = xbmcgui.Dialog().select('Choose Source Type', options)

    path = None
    if choice == 0:
        # URL ইনপুট বক্স
        path = xbmcgui.Dialog().input('Enter XML URL:')
    elif choice == 1:
        # সরাসরি ফোনের লোকাল ফাইল ব্রাউজার ওপেন হবে
        path = xbmcgui.Dialog().browse(1, 'Select Local Movie XML File', 'files', '.xml')

    # ৩. যদি পাথ বা ইউআরএল পাওয়া যায় তবে সেভ করা
    if path:
        current_data = ADDON.getSetting('xml_list')
        try:
            xml_list = json.loads(current_data) if current_data else []
        except:
            xml_list = []

        xml_list.append({'name': name, 'path': path})
        ADDON.setSetting('xml_list', json.dumps(xml_list))
        
        xbmcgui.Dialog().notification('Success', f'"{name}" Added!', ICON, 3000)
        xbmc.executebuiltin('Container.Refresh') # মেনু আপডেট করার জন্য
    else:
        xbmcgui.Dialog().notification('Cancelled', 'Nothing was selected', ICON, 2000)

def delete_xml_file():
    if xbmcgui.Dialog().yesno('Confirm Delete', 'Delete ALL custom added directories?'):
        ADDON.setSetting('xml_list', '[]')
        xbmcgui.Dialog().notification('Deleted', 'All paths cleared!', ICON, 3000)
        xbmc.executebuiltin('Container.Refresh')


def show_years():
    movies = load_movies()
    years = sorted(set(str(m['year']) for m in movies), reverse=True)

    for year in years:
        item = xbmcgui.ListItem(f"[B][COLOR lime]{year}[/COLOR][/B]")
        item.setArt({'icon': ICON, 'thumb': ICON, 'poster': ICON, 'fanart': ICON})
        xbmcplugin.addDirectoryItem(HANDLE, get_url(action='movies_by_year', year=year), item, True)
    xbmcplugin.endOfDirectory(HANDLE)


def list_movies_by_year(year):
    movies = load_movies()
    filtered = [m for m in movies if str(m['year']) == str(year)]
    display_movies(filtered)
    xbmcplugin.endOfDirectory(HANDLE)


def list_all_movies(page=1, custom_path=None):
    try:
        per_page = int(ADDON.getSetting('items_per_page'))
    except:
        per_page = 20

    # যদি কাস্টম পাথ থাকে তবে সেটি থেকে লোড হবে, নাহলে মেইন থেকে
    movies = load_movies(custom_path)
    start = (page - 1) * per_page
    end = start + per_page

    display_movies(movies[start:end])

    if end < len(movies):
        next_item = xbmcgui.ListItem("[B][COLOR gold]Next Page >>[/COLOR][/B]")
        url_params = {'action': 'all_movies', 'page': page + 1}
        if custom_path: url_params['custom_path'] = custom_path
        
        xbmcplugin.addDirectoryItem(HANDLE, get_url(**url_params), next_item, True)
    xbmcplugin.endOfDirectory(HANDLE)


def run_search():
    query = xbmcgui.Dialog().input('Search Movie')
    if not query: return
    movies = load_movies()
    results = [m for m in movies if query.lower() in m['title'].lower()]
    display_movies(results)
    xbmcplugin.endOfDirectory(HANDLE)


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
    elif action == 'custom_view':
        # নতুন পাথ থেকে মুভি দেখানোর জন্য
        list_all_movies(page=1, custom_path=params.get('custom_path'))
    elif action == 'add_xml':
        add_xml_file()
    elif action == 'delete_xml':
        delete_xml_file()
    else:
        show_main_menu()