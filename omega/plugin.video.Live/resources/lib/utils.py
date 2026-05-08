# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, os, xbmcgui, xbmcplugin, sys, re, xbmcaddon

# প্লাগিন সেটিংস এবং পাথ
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path, 'icon.png')
default_fanart = os.path.join(addon_path, 'fanart.jpg')

# অপ্রয়োজনীয় ফাইল ইগনোর করার লিস্ট
EXCLUDE_LIST = ['h5ai', 'styles.css', 'favicon', 'css', 'js', 'fonts', 'index', 'cgi-bin', '..', 'parent directory', 'browsehappy.com']

def get_year(name):
    match = re.search(r'\b(20\d{2}|19\d{2})\b', name)
    return int(match.group()) if match else 0

def is_main_year_folder(name):
    return bool(re.match(r'^\(\d{4}\)', name.strip()))

def get_links(url):
    try:
        if not url.endswith('/'): url += '/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=["\']?([^"\' >]+)["\']?', html)
            unique_links = list(set([urllib.parse.urljoin(url, link) for link in links 
                                   if not any(x in link for x in ['../', './', '/?']) 
                                   and 'C=' not in link and 'O=' not in link]))
            return unique_links
    except:
        return []

def get_smart_poster(folder_url, folder_name):
    clean_name = os.path.basename(folder_name.rstrip('/'))
    possible_posters = ["a_AL_.jpg", "poster.jpg", "folder.jpg", clean_name + ".jpg", "cover.jpg"]
    
    links = get_links(folder_url)
    img_map = {os.path.basename(urllib.parse.unquote(l)): l for l in links if l.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))}

    for p_name in possible_posters:
        if p_name in img_map:
            return img_map[p_name]
    
    for l in links:
        if l.lower().endswith(('.jpg', '.jpeg', '.png', '.tbn')):
            return l
    return None

def list_items(url, addon_handle, custom_icon=None):
    all_links = get_links(url)
    folders = []
    files = []
    current_dir_images = {} 
    
    active_icon = custom_icon if custom_icon else icon_path

    for l in all_links:
        name = os.path.basename(urllib.parse.unquote(l).rstrip('/'))
        if any(item in name.lower() for item in EXCLUDE_LIST): continue
        
        if l.lower().endswith(('.jpg', '.jpeg', '.png', '.tbn')):
            name_no_ext = os.path.splitext(name.lower())[0]
            current_dir_images[name_no_ext] = l
            continue 

        if l.endswith('/'): folders.append(l)
        else: files.append(l)

    folders.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)
    files.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)

    # ফোল্ডার ডিসপ্লে
    for full_url in folders:
        clean_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        if is_main_year_folder(clean_name):
            thumb = active_icon
            fanart = default_fanart # মেইন ইয়ার ফোল্ডারে ডিফল্ট ফ্যানআর্ট
        else:
            thumb = get_smart_poster(full_url, clean_name) or active_icon
            fanart = thumb # মুভি ফোল্ডারে পোস্টারটিই ফ্যানআর্ট হবে

        li = xbmcgui.ListItem(label="[COLOR skyblue]📁 %s[/COLOR]" % clean_name)
        # ফ্যানআর্ট আপডেট করা হয়েছে
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': "DefaultFolder.png", 'fanart': fanart})
        url_param = sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(full_url)
        xbmcplugin.addDirectoryItem(addon_handle, url_param, li, True)

    # ফাইল ডিসপ্লে
    for full_url in files:
        if not full_url.lower().endswith(('.mp4', '.mkv', '.avi', '.ts', '.webm')):
            continue

        clean_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        file_no_ext = os.path.splitext(clean_name.lower())[0]
        
        li = xbmcgui.ListItem(label="[COLOR springgreen]▶ %s[/COLOR]" % clean_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'title': clean_name, 'mediatype': 'movie'})
        
        video_thumb = current_dir_images.get(file_no_ext)
        if not video_thumb and current_dir_images:
            video_thumb = list(current_dir_images.values())[0]
        
        thumb = video_thumb or active_icon
        # ফ্যানআর্ট আপডেট করা হয়েছে যাতে মুভির পোস্টার ব্যাকগ্রাউন্ডে দেখায়
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb, 'fanart': thumb})
        xbmcplugin.addDirectoryItem(addon_handle, full_url, li, False)
            
    xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
    handle = int(sys.argv[1])
    paramstring = sys.argv[2][1:]
    params = urllib.parse.parse_qs(paramstring)
    
    action = params.get('action', [None])[0]
    target_url = params.get('url', [None])[0]

    if action == 'list_items':
        list_items(target_url, handle, icon_path)