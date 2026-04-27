# -*- coding: utf-8 -*-

# Author/Copyright: fr33p0rt (based on code by Roman V. M.)
# License: GPLv3 https://www.gnu.org/copyleft/gpl.html

import os
import sys
import re
import requests
import random
import six

from six.moves import urllib
from six.moves import urllib_parse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from resources.lib.pornky.pornky import Pornky
from resources.lib.browser.browser import Browser
from resources.lib.cfg.filter import Filter
from resources.lib.cfg.res import Res
from resources.lib.cfg.cfg import Cfg

from contextlib import contextmanager

__addon_version__ = '0.9.13'
__addon_name__ = 'pornky.club (free)'
__addon_id__ = 'plugin.video.club.pornky.free'

@contextmanager
def busy_dialog():
    kodi_version = re.findall(r'[0-9.]+|$', xbmc.getInfoLabel('System.BuildVersion'))[0]
    if int(kodi_version.split('.')[0]) >= 18:
        dialog = 'busydialognocancel'
    else:
        dialog = 'busydialog'

    xbmc.executebuiltin('ActivateWindow({})'.format(dialog))
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close({})'.format(dialog))


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urllib_parse.urlencode(kwargs))


def get_categories():
    return pornky.get_categories()


def get_videos(url):
    return pornky.get_videos_and_next_page(url)


def list_end():
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(_handle)


def list_root():
    xbmcplugin.setPluginCategory(_handle, 'pornky.club')
    xbmcplugin.setContent(_handle, 'videos')
    main_menu = pornky.get_main_menu()

    if pornky.last_status_code != 200:
        xbmcgui.Dialog().ok('Communication error', 'Addon is not able to communicate with remote site, error %s' %
                            pornky.last_status_code)
        exit(0)

    log_menu = pornky.get_log_menu()

    for menu_item in log_menu:
        list_item = xbmcgui.ListItem(label=menu_item['name'])
        list_item.setInfo('video', {'title': menu_item['name'],
                                    'genre': menu_item['name'],
                                    'mediatype': 'video'})

        url = get_url(action='listing', category=menu_item['url'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem('Search menu ...')
    list_item.setInfo('video', {'title': 'Search menu ...',
                                'genre': 'Search menu ...',
                                'mediatype': 'video'})
    url = get_url(action='searchmenu', category='')
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    
    for menu_item in main_menu:
        list_item = xbmcgui.ListItem(label=menu_item['name'])
        list_item.setInfo('video', {'title': menu_item['name'],
                                    'genre': menu_item['name'],
                                    'mediatype': 'video'})

        if menu_item['name'][0:7] == 'Categor':
            url = get_url(action='categories', category='')
        else:
            url = get_url(action='listing', category=menu_item['url'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_videos('')


def list_categories():
    xbmcplugin.setPluginCategory(_handle, 'Categories')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()
    for category in categories:
        if (cfg.filter == Filter.SUPPRESS and category['name'] not in cfg.filter_items) or\
                (cfg.filter == Filter.ONLY and category['name'] in cfg.filter_items) or\
                 cfg.filter == Filter.OFF:
            list_item = xbmcgui.ListItem(label=category['name'])
            list_item.setArt({'thumb': category['thumb'] if cfg.show_category_image else None,
                              'icon': category['thumb'] if cfg.show_category_image else None})
            list_item.setInfo('video', {'title': category['name'],
                                        'genre': category['name'],
                                        'mediatype': 'video'})
            list_item.setProperty('IsPlayable', 'true')
            url = get_url(action='listing', category=category['url'])
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_end()


def list_videos(url):
    xbmcplugin.setPluginCategory(_handle, url if url[:4] != 'http' else '/'.join(url.split('/')[3:]))
    xbmcplugin.setContent(_handle, 'videos')
    videos, next_page = get_videos(url)

    for video in videos:
        list_item = xbmcgui.ListItem(label=video['name'])
        list_item.setInfo('video', {'title': '%s (%s)' % (video['name'], video['duration']),
                                    'genre': video['categories'],
                                    'mediatype': 'video'})
        list_item.setArt({'thumb': video['thumb'] if cfg.show_video_image else None,
                          'icon': video['thumb'] if cfg.show_video_image else None,
                          'fanart': video['thumb'] if cfg.show_video_background else None})

        url_download = get_url(action='download', video_page=video['page'], video_name=video['name'])
        context_menu_download = ('Download video', 'RunPlugin({})'.format(url_download))

        url_browser = get_url(action='browser', video_page=video['page'], video_name=video['name'])
        context_menu_open = ('Open video in browser', 'RunPlugin({})'.format(url_browser))

        list_item.addContextMenuItems([context_menu_open, context_menu_download])
        list_item.setProperty('IsPlayable', 'true')
        
        url_play = get_url(action='play', video=video['page'])
        xbmcplugin.addDirectoryItem(_handle, url_play, list_item, False)

    if next_page:
        list_item = xbmcgui.ListItem(label=next_page['name'])
        list_item.setInfo('video', {'title': next_page['name'],
                                    'genre': next_page['name'],
                                    'mediatype': 'video'})
        url_next = get_url(action='listing', category=next_page['url'])
        xbmcplugin.addDirectoryItem(_handle, url_next, list_item, True)
    list_end()


def search_dialog():
    keyboard = xbmc.Keyboard('', "Search")
    keyboard.doModal()
    if not keyboard.isConfirmed():
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    query = urllib.quote('%s' % search_string)
    search_url = pornky.URL_SEARCH % query
    list_videos(search_url)


def search_menu():
    xbmcplugin.setPluginCategory(_handle, 'Search')
    xbmcplugin.setContent(_handle, 'videos')

    list_item = xbmcgui.ListItem('Search form ...')
    list_item.setInfo('video', {'title': 'Search',
                                'genre': 'Search form ...',
                                'mediatype': 'video'})
    url = get_url(action='search', category='')
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    for i in cfg.search_items:
        list_item = xbmcgui.ListItem(label=i)
        list_item.setInfo('video', {'title': i,
                                    'genre': i,
                                    'mediatype': 'video'})
        url = get_url(action='listing', category='search/?q='+i)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_end()


def play_video(path):
    video = pornky.get_video_link(path, cfg.res.res())
    play_item = xbmcgui.ListItem(path=video[1])
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(urllib_parse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            list_videos(params['category'])
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'categories':
            list_categories()
        elif params['action'] == 'searchmenu':
            search_menu()
        elif params['action'] == 'search':
            search_dialog()
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_root()


def router_special(paramstring):
    params = dict(urllib_parse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'download':
            res = Res(int(xbmcaddon.Addon(id=_id).getSetting('res')))
            download_path = xbmcaddon.Addon(id=_id).getSetting('download_path')
            if not download_path:
                xbmcgui.Dialog().ok('Download Error!', 'Download path is not set!')
                return

            video_url = pornky.get_video_link(params['video_page'], res.res())[1]
            video_name = re.sub('[^0-9A-Za-z _-]+', '', params['video_name']).replace(' ', '_')

            result = 'Download Error!'
            with busy_dialog():
                try:
                    r = requests.get(video_url)
                    with open(os.path.join(download_path, video_name + '.mp4'), "wb") as video_file:
                        video_file.write(r.content)
                    result = 'Download Complete!'
                except:
                    pass
            xbmcgui.Dialog().ok(result, result)
        if params['action'] == 'browser':
            browser = Browser()
            browser.open(params['video_page'])


_url = sys.argv[0]
_id = _url.replace('plugin://', '').replace('/', '')
_handle = int(sys.argv[1])

if __name__ == '__main__':
    pornky = Pornky()

    if _handle == -1:
        router_special(sys.argv[2][1:])
    else:
        cfg = Cfg()
        cfg.res = Res(int(xbmcplugin.getSetting(_handle, 'res')))
        cfg.search_items = xbmcplugin.getSetting(_handle, 'search_items').split(',')
        cfg.filter = Filter(int(xbmcplugin.getSetting(_handle, 'filter')))
        cfg.filter_items = xbmcplugin.getSetting(_handle, 'filter_items').split(',')
        cfg.username = xbmcplugin.getSetting(_handle, 'username')
        cfg.password = xbmcplugin.getSetting(_handle, 'password')
        cfg.cookie_PHPSESSID = xbmcplugin.getSetting(_handle, 'cookie_PHPSESSID')
        cfg.disable_login = xbmcplugin.getSetting(_handle, 'disable_login') == 'true'

        logged_in, cookies = pornky.set_cookies(cfg)
        if logged_in and cookies:
            xbmcaddon.Addon(_id).setSetting(id='cookie_PHPSESSID', value=cookies['PHPSESSID'])
        
        cfg.prefix_overwrite = xbmcplugin.getSetting(_handle, 'prefix_overwrite') == 'true'
        cfg.show_category_image = xbmcplugin.getSetting(_handle, 'show_category_image') == 'true'
        cfg.show_video_image = xbmcplugin.getSetting(_handle, 'show_video_image') == 'true'
        cfg.show_video_background = xbmcplugin.getSetting(_handle, 'show_video_background') == 'true'

        router(sys.argv[2][1:])