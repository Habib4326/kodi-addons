# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, os, xbmcgui, xbmcplugin, xbmc, re, sys

def get_links(url):
    try:
        if not url.endswith('/'): url += '/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href=["\']?([^"\' >]+)["\']?', html)
            clean_links = []
            for link in links:
                if link in ['../', './', '/'] or link.startswith('?') or link.startswith('#'): continue
                if 'C=' in link or 'O=' in link or 'Parent' in link: continue
                if not link.startswith('http'):
                    full_link = urllib.parse.urljoin(url, link)
                else:
                    full_link = link
                clean_links.append(full_link)
            return list(set(clean_links))
    except:
        return []

def list_items(url, addon_handle, icon_path):
    links = get_links(url)
    if not links:
        xbmcgui.Dialog().notification("Info", "ফোল্ডারটি খালি", xbmcgui.NOTIFICATION_INFO, 3000)
        return

    for full_url in links:
        clean_name = os.path.basename(urllib.parse.unquote(full_url).rstrip('/'))
        
        if full_url.endswith('/'):
            # ফোল্ডার আইকন
            li = xbmcgui.ListItem(label=clean_name)
            li.setArt({'icon': 'DefaultFolder.png'}) 
            xbmcplugin.addDirectoryItem(addon_handle, sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(full_url), li, True)
        elif any(full_url.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.ts', '.mov']):
            # ভিডিও ফাইল আইকন
            li = xbmcgui.ListItem(label=clean_name)
            li.setArt({'icon': 'DefaultVideo.png'})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(addon_handle, full_url, li, False)
            
    xbmcplugin.endOfDirectory(addon_handle)