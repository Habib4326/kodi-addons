# -*- coding: utf-8 -*-
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, urllib.parse, random, re
from resources.lib import utils
from resources.lib.servers import circle, dhakaflix, infomedia, moviedata, korean, iccftp

addon = xbmcaddon.Addon()
handle = int(sys.argv[1])
addon_path = addon.getAddonInfo('path')

# আইকন পাথ সেট করা হলো
icon = os.path.join(addon_path, 'icon.png')
fanart = os.path.join(addon_path, 'fanart.jpg')

# হলুদ ফোল্ডার আইকনের জন্য আলাদা পাথ
yellow_folder = os.path.join(addon_path, 'resources', 'media', 'folder.png')

# যদি folder.png না থাকে, তবে ডিফল্ট icon ব্যবহার করবে
if not os.path.exists(yellow_folder):
    yellow_folder = icon

COLORS = ['red', 'green', 'deepskyblue', 'yellow', 'orange', 'cyan', 'lime', 'gold', 'magenta', 'chartreuse']

def get_styled_label(text):
    """টেক্সট ক্লিন করে র্যান্ডম কালার এবং বোল্ড সেট করবে"""
    color = random.choice(COLORS)
    clean_text = re.sub(r'\[/?(?:COLOR|B).*?\]', '', text).strip()
    return f"[COLOR {color}][B]{clean_text}[/B][/COLOR]"

def router(paramstring):
    params = urllib.parse.parse_qs(paramstring)
    action = params.get('action', [None])[0]
    
    if action == 'list_servers':
        name = params.get('name', [None])[0]
        mod = {'CIRCLE': circle, 'DHAKAFLIX': dhakaflix, 'INFO': infomedia, 
               'MOVIE': moviedata, 'KOREAN': korean, 'ICC': iccftp}.get(name)
        if mod:
            for label, url in mod.SERVERS:
                li = xbmcgui.ListItem(label=get_styled_label(label))
                # সার্ভার লিস্টের জন্য হলুদ ফোল্ডার সেট
                li.setArt({'icon': yellow_folder, 'thumb': yellow_folder, 'fanart': fanart})
                xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(url), li, True)
        xbmcplugin.endOfDirectory(handle)
        
    elif action == 'list_items':
        url = params.get('url', [None])[0]
        if url:
            # সাব-আইটেম বা ইয়ার লিস্টের জন্য এখানে yellow_folder পাঠানো হয়েছে
            utils.list_items(url, handle, yellow_folder)
        
    else:
        cats = [("CIRCLE", "enable_circle"), ("DHAKAFLIX", "enable_dhaka"), 
                ("INFO", "enable_info"), ("MOVIE", "enable_movie"), 
                ("KOREAN", "enable_korean"), ("ICC", "enable_icc")]
        for name, setting in cats:
            if addon.getSetting(setting) == 'true':
                li = xbmcgui.ListItem(label=get_styled_label(name))
                # মেইন মেনুর জন্যও হলুদ ফোল্ডার আইকন সেট
                li.setArt({'icon': yellow_folder, 'thumb': yellow_folder, 'fanart': fanart})
                xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?action=list_servers&name=' + name, li, True)
        xbmcplugin.endOfDirectory(handle)

if __name__ == '__main__':
    router(sys.argv[2][1:])