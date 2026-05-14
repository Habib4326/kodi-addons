# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, os, xbmcgui, xbmcplugin, sys, re, xbmcaddon, html

# প্লাগিন সেটিংস এবং পাথ
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
icon_path = os.path.join(addon_path, 'icon.png')
default_fanart = os.path.join(addon_path, 'fanart.jpg')

# অপ্রয়োজনীয় ফাইল ইগনোর করার লিস্ট
EXCLUDE_LIST = ['h5ai', 'styles.css', 'favicon', 'css', 'js', 'fonts', 'index', 'cgi-bin', '..', 'parent directory', 'browsehappy.com']

def get_styled_label(text):
    """টেক্সট ক্লিন করে নিয়ন গ্রিন কালার দেবে"""
    color = 'lime' 
    # HTML entities পরিষ্কার করা (যেমন &amp; কে & করা)
    clean_text = html.unescape(text)
    clean_text = re.sub(r'\[/?(?:COLOR|B).*?\]', '', clean_text).strip()
    return f"[COLOR {color}][B]{clean_text}[/B][/COLOR]"

def get_year(name):
    match = re.search(r'\b(20\d{2}|19\d{2})\b', name)
    return int(match.group()) if match else 0

def is_main_year_folder(name):
    return bool(re.match(r'^\(\d{4}\)', name.strip()))

def get_links(url):
    """ডিসকভারি এফটিপির লিঙ্ক এক্সট্রাক্ট করার সবচেয়ে নিরাপদ পদ্ধতি"""
    try:
        # URL-এ স্পেস থাকলে তা এনকোড করা
        url = url.replace(' ', '%20')
        if not url.endswith('/'): url += '/'
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=[\'"]?([^\'" >]+)[\'"]?', html_content)
            
            unique_links = []
            for link in links:
                if any(x in link.lower() for x in ['../', './', '/?', 'c=', 'o=', 's=', 'n=']): continue
                
                full_url = urllib.parse.urljoin(url, link)
                if full_url not in unique_links and full_url.rstrip('/') != url.rstrip('/'):
                    unique_links.append(full_url)
            return unique_links
    except:
        return []

def get_smart_poster(folder_url, folder_name):
    """মুভি ফোল্ডারের ভেতর থেকে পোস্টার ইমেজ খুঁজে বের করা"""
    try:
        links = get_links(folder_url)
        if not links: return None
        
        clean_name = os.path.basename(folder_name.rstrip('/'))
        possible_posters = ["a_AL_.jpg", "poster.jpg", "folder.jpg", clean_name + ".jpg", "cover.jpg"]
        
        img_map = {os.path.basename(urllib.parse.unquote(l)): l for l in links if l.lower().endswith(('.jpg', '.jpeg', '.png'))}

        for p_name in possible_posters:
            if p_name in img_map: return img_map[p_name]
        
        for l in links:
            if l.lower().endswith(('.jpg', '.jpeg', '.png')) and 'fanart' not in l.lower():
                return l
    except: pass
    return None

def list_items(url, addon_handle, custom_icon=None):
    all_links = get_links(url)
    folders = []
    files = []
    current_dir_images = {} 
    
    active_icon = custom_icon if custom_icon else icon_path

    for l in all_links:
        raw_name = os.path.basename(urllib.parse.unquote(l).rstrip('/'))
        name = html.unescape(raw_name)
        
        if not name or any(item in name.lower() for item in EXCLUDE_LIST): continue
        
        if l.lower().endswith(('.jpg', '.jpeg', '.png')):
            name_no_ext = os.path.splitext(name.lower())[0]
            current_dir_images[name_no_ext] = l
            continue 

        if l.endswith('/'): folders.append(l)
        else:
            if l.lower().endswith(('.mp4', '.mkv', '.avi', '.ts', '.webm')):
                files.append(l)

    # সর্টিং
    folders.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)
    files.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)

    for full_url in folders:
        raw_folder_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        clean_name = html.unescape(raw_folder_name)
        styled_name = get_styled_label("📁 " + clean_name)
        
        if is_main_year_folder(clean_name):
            thumb = active_icon
            fanart = default_fanart
        else:
            found_poster = get_smart_poster(full_url, clean_name)
            thumb = found_poster if found_poster else active_icon
            fanart = found_poster if found_poster else default_fanart

        li = xbmcgui.ListItem(label=styled_name)
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': active_icon, 'fanart': fanart})
        
        url_param = sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(full_url)
        xbmcplugin.addDirectoryItem(addon_handle, url_param, li, True)

    # ভিডিও ফাইল ডিসপ্লে
    for full_url in files:
        raw_file_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        clean_name = html.unescape(raw_file_name)
        file_no_ext = os.path.splitext(clean_name.lower())[0]
        styled_file_name = get_styled_label("▶ " + clean_name)
        
        li = xbmcgui.ListItem(label=styled_file_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'title': clean_name, 'mediatype': 'movie'})
        
        video_thumb = current_dir_images.get(file_no_ext)
        if not video_thumb and current_dir_images:
            video_thumb = list(current_dir_images.values())[0]
        
        thumb = video_thumb if video_thumb else active_icon
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb, 'fanart': thumb})
        
        # লগ অনুযায়ী সমস্যা সমাধান: লিঙ্ক থেকে HTML entities (&amp;) পরিষ্কার করা
        # এবং স্পেসকে %20 দিয়ে রিপ্লেস করা
        final_play_url = html.unescape(full_url).replace(' ', '%20')
        
        xbmcplugin.addDirectoryItem(addon_handle, final_play_url, li, False)
            
    xbmcplugin.endOfDirectory(addon_handle)