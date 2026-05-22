import sys
import urllib.parse
import xbmcgui
import xbmcplugin

def get_args():
    """কোডি থেকে পাঠানো প্যারামিটার ডিকোড করে।"""
    args = urllib.parse.parse_qs(sys.argv[2][1:])
    return {k: v[0] for k, v in args.items()}

def add_directory_item(handle, name, mode, url="", poster="", is_folder=True):
    """কোডি স্ক্রিনে একটি ফোল্ডার বা ভিডিও আইটেম যোগ করে।"""
    base_url = sys.argv[0]
    param_url = urllib.parse.urlencode({'mode': mode, 'url': url, 'title': name, 'poster': poster})
    item_url = f"{base_url}?{param_url}"
    
    list_item = xbmcgui.ListItem(label=name)
    if poster:
        list_item.setArt({'thumb': poster, 'poster': poster, 'icon': poster})
        
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        
    xbmcplugin.addDirectoryItem(handle=handle, url=item_url, listitem=list_item, isFolder=is_folder)