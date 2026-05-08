# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
from xbmcvfs import translatePath
import os
import shutil

addon = xbmcaddon.Addon()

home = translatePath('special://home/')
addon_data_path = os.path.join(home, 'userdata/addon_data')


def get_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total


def format_size(size):
    return f"{round(size / (1024*1024), 2)} MB"


# Storage Analyzer
def analyze_storage():
    dialog = xbmcgui.Dialog()

    results = []

    for folder in os.listdir(addon_data_path):
        path = os.path.join(addon_data_path, folder)
        size = get_size(path)
        results.append((folder, size))

    results.sort(key=lambda x: x[1], reverse=True)

    top = results[:10]

    display = [f"{name} - {format_size(size)}" for name, size in top]

    dialog.ok("Top Storage Usage", "\n".join(display))


# Smart Clean
def smart_clean():
    xbmc.executebuiltin('RunScript(plugin.program.smartcleaner)')


def delete_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


# GUI
class SmartCleanerGUI(xbmcgui.WindowXML):

    def onInit(self):
        pass

    def onClick(self, controlId):

        if controlId == 1:
            xbmc.executebuiltin('Notification(Cleaner, Running Smart Clean)')
            smart_clean()

        elif controlId == 2:
            analyze_storage()

        elif controlId == 3:
            delete_folder(translatePath('special://temp/'))
            xbmcgui.Dialog().ok("Done", "Temp cleaned")

        elif controlId == 4:
            delete_folder(translatePath('special://thumbnails/'))
            xbmcgui.Dialog().ok("Done", "Thumbnails cleaned")


if __name__ == "__main__":
    ui = SmartCleanerGUI("script-smartcleaner.xml", addon.getAddonInfo('path'))
    ui.doModal()
    del ui