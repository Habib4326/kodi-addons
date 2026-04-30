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

# আইকন এবং ফ্যানআর্টের পাথ (আপনার অ্যাডঅন ফোল্ডারে এই ফাইলগুলো থাকতে হবে)
ICON = os.path.join(ADDON_PATH, "icon.png")
FANART_DEFAULT = os.path.join(ADDON_PATH, "fanart.jpg")

# যদি ফোল্ডারের জন্য বিশেষ কোনো অনলাইন আইকন ব্যবহার করতে চান
FOLDER_ICON = "https://raw.githubusercontent.com/google/material-design-icons/master/png/file/folder/materialicons/48dp/1x/baseline_folder_black_48dp.png"

def get_url(**kwargs):
    return BASE_URL + '?' + urllib.parse.urlencode(kwargs)

def load_movies_by_year():
    movie_dict = {}
    try:
        response = urllib.request.urlopen(XML_URL)
        xml_data = response.read()
        root = ET.fromstring(xml_data)

        for movie in root.findall("movie"):
            year = movie.findtext("year", "Unknown")
            movie_item = {
                "title": movie.findtext("title", "Unknown"),
                "link": movie.findtext("link", ""),
                "poster": movie.findtext("poster", ""),
                "rating": movie.findtext("rating", "N/A")
            }
            if year not in movie_dict:
                movie_dict[year] = []
            movie_dict[year].append(movie_item)
    except Exception as e:
        xbmcgui.Dialog().ok("Error", "XML Load Error: " + str(e))
    return movie_dict

def show_main_menu():
    """মেনু আইটেম যেখানে আইকন এবং ফ্যানআর্ট সেট করা হয়েছে"""
    
    # সার্চ অপশন
    search_item = xbmcgui.ListItem(label='🔍 Search Movie')
    search_item.setArt({
        'icon': ICON, 
        'thumb': ICON, 
        'fanart': FANART_DEFAULT
    })
    xbmcplugin.addDirectoryItem(HANDLE, get_url(action='search'), search_item, True)

    movie_dict = load_movies_by_year()
    sorted_years = sorted(movie_dict.keys(), reverse=True)

    for year in sorted_years:
        list_item = xbmcgui.ListItem(label=u'📁 Year: {}'.format(year))
        
        # এখানে ফোল্ডারের জন্য আইকন এবং ফ্যানআর্ট সেট করা হচ্ছে
        # আপনি চাইলে প্রতিটি বছরের জন্য আলাদা ইমেজ দিতে পারেন, এখানে ডিফল্ট ব্যবহার করা হয়েছে
        list_item.setArt({
            'icon': FOLDER_ICON,
            'thumb': FOLDER_ICON,
            'poster': FOLDER_ICON,
            'fanart': FANART_DEFAULT  # এখানে আপনার পছন্দমতো ব্যাকগ্রাউন্ড ইমেজ দিতে পারেন
        })
        
        url = get_url(action='list_year_movies', year_val=year)
        xbmcplugin.addDirectoryItem(HANDLE, url, list_item, True)

    xbmcplugin.endOfDirectory(HANDLE)

def list_year_movies(year):
    movie_dict = load_movies_by_year()
    movies = movie_dict.get(year, [])

    for movie in movies:
        list_item = xbmcgui.ListItem(label=movie['title'])
        poster = movie.get('poster') if movie.get('poster') else ICON
        
        list_item.setArt({
            'thumb': poster,
            'poster': poster,
            'fanart': poster # মুভি সিলেক্ট করলে ব্যাকগ্রাউন্ডে পোস্টার দেখাবে
        })
        
        list_item.setInfo('video', {
            'title': movie['title'],
            'year': int(year) if year.isdigit() else 0,
            'mediatype': 'movie'
        })
        list_item.setProperty('IsPlayable', 'true')
        
        xbmcplugin.addDirectoryItem(HANDLE, movie['link'], list_item, False)

    xbmcplugin.endOfDirectory(HANDLE)

# ... (বাকি ফাংশনগুলো আগের মতোই থাকবে)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params:
        if params.get('action') == 'search':
            # run_search ফাংশনটি এখানে কল হবে
            pass 
        elif params.get('action') == 'list_year_movies':
            list_year_movies(params.get('year_val'))
    else:
        show_main_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])