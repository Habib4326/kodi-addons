# -*- coding: utf-8 -*-
import sys, xbmcplugin, xbmcgui, xbmcaddon, os, urllib.parse
from resources.lib import utils
from resources.lib.servers import circle, dhakaflix, infomedia, moviedata, korean, iccftp

addon = xbmcaddon.Addon()
handle = int(sys.argv[1])
icon = os.path.join(addon.getAddonInfo('path'), 'icon.png')

def router(paramstring):
    params = urllib.parse.parse_qs(paramstring)
    action = params.get('action', [None])[0]
    
    if action == 'list_servers':
        name = params.get('name', [None])[0]
        mod = {'CIRCLE': circle, 'DHAKAFLIX': dhakaflix, 'INFO': infomedia, 
               'MOVIE': moviedata, 'KOREAN': korean, 'ICC': iccftp}.get(name)
        if mod:
            for label, url in mod.SERVERS:
                li = xbmcgui.ListItem(label=label)
                li.setArt({'icon': icon, 'thumb': icon})
                xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?action=list_items&url=' + urllib.parse.quote_plus(url), li, True)
        xbmcplugin.endOfDirectory(handle)
        
    elif action == 'list_items':
        url = params.get('url', [None])[0]
        if url:
            utils.list_items(url, handle, icon)
        
    else:
        cats = [("CIRCLE", "enable_circle"), ("DHAKAFLIX", "enable_dhaka"), 
                ("INFO", "enable_info"), ("MOVIE", "enable_movie"), 
                ("KOREAN", "enable_korean"), ("ICC", "enable_icc")]
        for name, setting in cats:
            if addon.getSetting(setting) == 'true':
                li = xbmcgui.ListItem(label=name)
                li.setArt({'icon': icon, 'thumb': icon})
                xbmcplugin.addDirectoryItem(handle, sys.argv[0] + '?action=list_servers&name=' + name, li, True)
        xbmcplugin.endOfDirectory(handle)

if __name__ == '__main__':
    router(sys.argv[2][1:])