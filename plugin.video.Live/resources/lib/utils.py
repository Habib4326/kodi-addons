# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, os, xbmcgui, xbmcplugin, sys, re

# অপ্রয়োজনীয় ফাইল ইগনোর করার লিস্ট
EXCLUDE_LIST = ['h5ai', 'styles.css', 'favicon', 'css', 'js', 'fonts', 'index', 'cgi-bin', '..', 'parent directory', 'browsehappy.com']

def get_year(name):
    # ফোল্ডারের নাম থেকে বছর (2026, 2025, 2024...) বের করা
    match = re.search(r'\b(20\d{2}|19\d{2})\b', name)
    return int(match.group()) if match else 0

def is_main_year_folder(name):
    # ফোল্ডারের নাম যদি ঠিক (2014) বা (1995) & Before দিয়ে শুরু হয়, তাহলে True রিটার্ন করবে
    # এতে করে মেইন ডিরেক্টরিতে অহেতুক পোস্টার খুঁজবে না
    return bool(re.match(r'^\(\d{4}\)', name.strip()))

def get_links(url):
    try:
        if not url.endswith('/'): url += '/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=["\']?([^"\' >]+)["\']?', html)
            # ডুপ্লিকেট লিঙ্ক এড়াতে set ব্যবহার
            unique_links = list(set([urllib.parse.urljoin(url, link) for link in links 
                                   if not any(x in link for x in ['../', './', '/?']) 
                                   and 'C=' not in link and 'O=' not in link]))
            return unique_links
    except:
        return []

def get_any_image_from_folder(folder_url):
    # মুভি ফোল্ডারের ভেতরে ঢুকে প্রথম পাওয়া যেকোনো .jpg বা ছবি নিবে (কোনো নির্দিষ্ট নাম খুঁজবে না)
    links = get_links(folder_url)
    for l in links:
        if l.lower().endswith(('.jpg', '.jpeg', '.png', '.tbn')):
            return l
    return None

def list_items(url, addon_handle, icon_path):
    all_links = get_links(url)
    folders = []
    files = []
    current_dir_image = None # বর্তমান ফোল্ডারে কোনো ছবি আছে কিনা তা সেভ রাখার জন্য
    
    for l in all_links:
        name = os.path.basename(urllib.parse.unquote(l).rstrip('/'))
        if any(item in name.lower() for item in EXCLUDE_LIST): continue
        
        # বর্তমান ফোল্ডারে যদি কোনো ছবি থাকে, সেটা রেখে দিবে ভিডিওর পোস্টার করার জন্য
        if l.lower().endswith(('.jpg', '.jpeg', '.png', '.tbn')):
            if not current_dir_image:
                current_dir_image = l
            continue # ছবিগুলোকে লিস্টে আইটেম হিসেবে দেখানোর দরকার নেই

        if l.endswith('/'): folders.append(l)
        else: files.append(l)

    # বছর অনুযায়ী সাজানো
    folders.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)
    files.sort(key=lambda x: get_year(os.path.basename(urllib.parse.unquote(x).rstrip('/'))), reverse=True)

    added_items = set()

    # ফোল্ডার ডিসপ্লে
    for full_url in folders:
        if full_url in added_items: continue
        added_items.add(full_url)
        
        clean_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        
        # লজিক: ফোল্ডারটি যদি ইয়ার ফোল্ডার (মেইন ডিরেক্টরি) হয়, তাহলে পোস্টার খুঁজবে না
        if is_main_year_folder(clean_name):
            thumb = icon_path
        else:
            # মুভি ফোল্ডার হলে ভেতরে ঢুকে যেকোনো একটি .jpg খুঁজবে
            thumb = get_any_image_from_folder(full_url) or icon_path
        
        li = xbmcgui.ListItem(label=clean_name)
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb, 'fanart': thumb})
        xbmcplugin.addDirectoryItem(addon_handle, sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(full_url), li, True)

    # ভিডিও ফাইল ডিসপ্লে
    for full_url in files:
        if full_url in added_items: continue
        
        # শুধু ভিডিও ফাইলগুলোই লিস্টে দেখাবে (txt, nfo ইত্যাদি ইগনোর করবে)
        if not full_url.lower().endswith(('.mp4', '.mkv', '.avi', '.ts', '.webm')):
            continue

        added_items.add(full_url)
        
        clean_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        li = xbmcgui.ListItem(label=clean_name)
        li.setProperty('IsPlayable', 'true')
        li.setInfo('video', {'title': clean_name, 'mediatype': 'movie'})
        
        # ভিডিও ফাইলের পোস্টার হিসেবে একই ফোল্ডারে থাকা .jpg টি ব্যবহার করবে
        thumb = current_dir_image or icon_path
        li.setArt({'thumb': thumb, 'poster': thumb, 'icon': thumb})
        
        xbmcplugin.addDirectoryItem(addon_handle, full_url, li, False)
            
    xbmcplugin.endOfDirectory(addon_handle)