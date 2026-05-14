# -*- coding: utf-8 -*-
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, urllib.parse, random, re, html
from resources.lib import utils

# অ্যাডন অবজেক্ট এবং হ্যান্ডেল
addon = xbmcaddon.Addon()
handle = int(sys.argv[1])
addon_path = addon.getAddonInfo('path')

# আইকন এবং ফ্যানআর্ট পাথ
icon = os.path.join(addon_path, 'icon.png')
fanart = os.path.join(addon_path, 'fanart.jpg')

# হলুদ ফোল্ডার আইকন সেটআপ
yellow_folder = os.path.join(addon_path, 'resources', 'media', 'folder.png')
if not os.path.exists(yellow_folder):
    yellow_folder = icon

COLORS = ['red', 'green', 'deepskyblue', 'yellow', 'orange', 'cyan', 'lime', 'gold', 'magenta', 'chartreuse']

def get_styled_label(text):
    """টেক্সট ক্লিন করে র্যান্ডম কালার এবং বোল্ড সেট করবে"""
    # HTML entities (যেমন &amp;) ক্লিন করা
    clean_text = html.unescape(text)
    color = random.choice(COLORS)
    # যদি আগে থেকে কোনো কালার ট্যাগ থাকে তা রিমুভ করে ক্লিন করবে
    clean_text = re.sub(r'\[/?(?:COLOR|B).*?\]', '', clean_text).strip()
    return f"[COLOR {color}][B]{clean_text}[/B][/COLOR]"

def router(paramstring):
    params = urllib.parse.parse_qs(paramstring)
    action = params.get('action', [None])[0]
    
    # ১. সার্ভারের ভেতরের লিস্ট দেখা (যেমন: English, Hindi ইত্যাদি)
    if action == 'list_servers':
        name = params.get('name', [None])[0]
        try:
            import importlib
            # ডাইনামিক ইম্পোর্ট: servers ফোল্ডার থেকে ফাইল কল করবে
            module_name = f'resources.lib.servers.{name.lower()}'
            mod = importlib.import_module(module_name)
            
            if hasattr(mod, 'SERVERS'):
                for label, url in mod.SERVERS:
                    li = xbmcgui.ListItem(label=get_styled_label(label))
                    li.setArt({'icon': yellow_folder, 'thumb': yellow_folder, 'fanart': fanart})
                    # URL সঠিকভাবে এনকোড করে পাস করা যাতে utils.py তা ঠিকভাবে পায়
                    encoded_url = urllib.parse.quote_plus(url)
                    xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?action=list_items&url=' + encoded_url, li, True)
        except Exception as e:
            print(f"Error loading server module: {e}")
            
        xbmcplugin.endOfDirectory(handle)
        
    # ২. ফোল্ডার বা ভিডিওর লিস্ট দেখা (utils.py ব্যবহার করে)
    elif action == 'list_items':
        url = params.get('url', [None])[0]
        if url:
            # URL-টি utils.py তে পাঠানোর আগে একবার unquote করে নেওয়া নিরাপদ
            # এটি আপনার লগে দেখা যাওয়া %20 বা &amp; জনিত সমস্যা সমাধানে সাহায্য করবে
            final_url = urllib.parse.unquote(url)
            utils.list_items(final_url, handle, yellow_folder)
        
    # ৩. মেইন মেনু (যা প্রথমেই ওপেন হবে)
    else:
        server_dir = os.path.join(addon_path, 'resources', 'lib', 'servers')
        
        # যদি সার্ভার ফোল্ডার থাকে, তবে ভেতরের সব .py ফাইল মেনু হিসেবে দেখাবে
        if os.path.exists(server_dir):
            files = sorted(os.listdir(server_dir))
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    server_id = file.replace(".py", "")
                    # ফাইলের নামকে সুন্দরভাবে দেখানোর জন্য
                    display_name = server_id.upper().replace("_", " ")
                    
                    li = xbmcgui.ListItem(label=get_styled_label(display_name))
                    li.setArt({'icon': yellow_folder, 'thumb': yellow_folder, 'fanart': fanart})
                    xbmcplugin.addDirectoryItem(handle, sys.argv[0] + f'?action=list_servers&name={server_id}', li, True)
        
        xbmcplugin.endOfDirectory(handle)

if __name__ == '__main__':
    router(sys.argv[2][1:])