# -*- coding: utf-8 -*-
import os, xbmc, xbmcaddon, xbmcgui, xbmcvfs

def make_server():
    ADDON_ID = 'plugin.video.Live'
    try:
        addon = xbmcaddon.Addon(id=ADDON_ID)
    except:
        addon = xbmcaddon.Addon()

    # দুটি আলাদা ইনপুট বক্স থেকে নাম সংগ্রহ
    menu_name = addon.getSetting('new_server_name').strip()    # ১ নম্বর ইমেজের জন্য
    folder_label = addon.getSetting('folder_label').strip()  # ২ নম্বর ইমেজের জন্য
    url = addon.getSetting('new_server_url').strip()

    if not menu_name or not folder_label or not url:
        xbmcgui.Dialog().notification('Error', 'সবগুলো বক্স পূরণ করুন!', xbmcgui.NOTIFICATION_ERROR)
        return

    # ফিক্স: xbmc.translatePath এর বদলে xbmcvfs.translatePath ব্যবহার করা হয়েছে
    folder_path = xbmcvfs.translatePath(os.path.join('special://home/addons/', ADDON_ID, 'resources/lib/servers/'))
    
    if not os.path.exists(folder_path):
        xbmcvfs.mkdirs(folder_path) # অ্যান্ড্রয়েডের জন্য mkdirs বেশি নিরাপদ

    # ১ নম্বর স্ক্রিনশটের জন্য ফাইলের নাম
    file_name = menu_name.lower().replace(" ", "_") + ".py"
    full_path = os.path.join(folder_path, file_name)

    # ২ নম্বর স্ক্রিনশটের জন্য ডাইনামিক কন্টেন্ট
    content = f'''# -*- coding: utf-8 -*-
import random
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red"]

def get_clr():
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● {folder_label}[/B][/COLOR]" % get_clr(), "{url}"),
]
'''
    try:
        # ফাইল রাইট করার জন্য xbmcvfs ব্যবহার করা নিরাপদ
        f = xbmcvfs.File(full_path, 'w')
        f.write(content)
        f.close()
        
        xbmcgui.Dialog().ok("সফল হয়েছে", f"সার্ভার যুক্ত হয়েছে!\nমেনু: {menu_name}\nফোল্ডার: {folder_label}")
        
        # বক্স খালি করা
        addon.setSetting('new_server_name', '')
        addon.setSetting('folder_label', '')
        addon.setSetting('new_server_url', '')
    except Exception as e:
        xbmcgui.Dialog().notification('Error', str(e), xbmcgui.NOTIFICATION_ERROR)

def delete_server():
    ADDON_ID = 'plugin.video.Live'
    folder_path = xbmcvfs.translatePath(os.path.join('special://home/addons/', ADDON_ID, 'resources/lib/servers/'))
    
    if not os.path.exists(folder_path): return
    files = [f for f in os.listdir(folder_path) if f.endswith('.py') and f != '__init__.py']
    
    selected = xbmcgui.Dialog().select('সার্ভার ডিলিট করুন', files)
    if selected != -1:
        os.remove(os.path.join(folder_path, files[selected]))
        xbmcgui.Dialog().notification('Deleted', 'সার্ভার মুছে ফেলা হয়েছে!', xbmcgui.NOTIFICATION_INFO)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        delete_server()
    else:
        make_server()