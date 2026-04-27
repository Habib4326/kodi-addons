# -*- coding: utf-8 -*-
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import xbmcplugin
import xbmcgui
import xbmcaddon

# Kodi অ্যাড-অনের তথ্য লোড করুন
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

# --- সেটিংস থেকে URL পড়ুন ---
MAIN_XML_URL = addon.getSetting('master_xml_url') 

if not MAIN_XML_URL:
     MAIN_XML_URL = "https://raw.githubusercontent.com/Habib4326/Kodi-Pornky/main/Main-Master.xml" # আপনার ডিফল্ট Master.xml URL

# অ্যাড-অনের ডিফল্ট আইকন এবং ফ্যানার্ট
ADDON_ICON = addon.getAddonInfo('icon')
ADDON_FANART = addon.getAddonInfo('fanart')
# --- সেটিংস পড়া শেষ ---

def fetch_xml_data(xml_url):
    """নির্দিষ্ট XML ফাইল URL থেকে ডেটা ডাউনলোড করে পার্স করে এবং ElementTree root প্রদান করে।"""
    print(f"DEBUG: XML ডেটা আনার চেষ্টা করা হচ্ছে: {xml_url}")
    try:
        headers = {'User-Agent': 'Kodi/1.0'}
        req = urllib.request.Request(xml_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
        print(f"DEBUG: XML ডেটা সফলভাবে আনা হয়েছে (URL: {xml_url}), সাইজ: {len(xml_data)} বাইট।")
        root = ET.fromstring(xml_data)
        return root
    except urllib.error.URLError as e:
        error_message = f"XML ফাইল ডাউনলোড করতে সমস্যা: {str(e)}. URL: {xml_url}"
        print(f"ERROR: {error_message}")
        xbmcgui.Dialog().notification("Movie Club", error_message, xbmcgui.NOTIFICATION_ERROR)
        return None
    except ET.ParseError as e:
        error_message = f"XML পার্স করতে সমস্যা: {str(e)}. URL: {xml_url}"
        print(f"ERROR: {error_message}")
        xbmcgui.Dialog().notification("Movie Club", error_message, xbmcgui.NOTIFICATION_ERROR)
        return None
    except Exception as e:
        error_message = f"একটি অজানা সমস্যা: {str(e)}. URL: {xml_url}"
        print(f"ERROR: {error_message}")
        xbmcgui.Dialog().notification("Movie Club", error_message, xbmcgui.NOTIFICATION_ERROR)
        return None

def build_menu():
    """প্রধান মেনু তৈরি করে (যেমন: All Movies, English Movies ইত্যাদি)।"""
    print("DEBUG: প্রধান মেনু তৈরি করা হচ্ছে।")
    
    root_element = fetch_xml_data(MAIN_XML_URL)
    if root_element is None:
        xbmcgui.Dialog().notification("Movie Club", "প্রধান XML ফাইল লোড করা যায়নি। অনুগ্রহ করে অ্যাড-অনের সেটিংসে Master XML URL চেক করুন।", xbmcgui.NOTIFICATION_ERROR)
        print("ERROR: প্রধান মেনু তৈরি করা যায়নি কারণ Master XML লোড হয়নি।")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
        return

    # Master.xml এর জন্য <category> অথবা <item> উভয় ট্যাগই খুঁজে দেখবে
    categories = root_element.findall('category')
    if not categories:
        categories = root_element.findall('item')
    
    if not categories:
        xbmcgui.Dialog().notification("Movie Club", "কোন ক্যাটাগরি পাওয়া যায়নি। অনুগ্রহ করে Master XML ফাইলটি পরীক্ষা করুন।", xbmcgui.NOTIFICATION_WARNING)
        print("ERROR: প্রধান মেনু তৈরি করা যায়নি কারণ কোনো ক্যাটাগরি/আইটেম ট্যাগ পাওয়া যায়নি।")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
        return

    for category_element in categories:
        category_name = category_element.find('title').text if category_element.find('title') is not None else "Untitled Category"
        category_link_url = category_element.find('link').text if category_element.find('link') is not None else None
        
        category_thumb = category_element.find('thumb').text if category_element.find('thumb') is not None else None
        if not category_thumb:
            category_thumb = category_element.find('thumbnail').text if category_element.find('thumbnail') is not None else ADDON_ICON

        category_fanart = category_element.find('fanart').text if category_element.find('fanart') is not None else ADDON_FANART
        
        if not category_link_url:
            print(f"WARNING: '{category_name}' ক্যাটাগরির জন্য কোনো লিঙ্ক পাওয়া যায়নি, এটি এড়িয়ে যাওয়া হচ্ছে।")
            continue

        list_item = xbmcgui.ListItem(label=category_name)
        
        list_item.setArt({
            'thumb': category_thumb,
            'fanart': category_fanart,
            'icon': category_thumb 
        })

        encoded_category_url = urllib.parse.quote_plus(category_link_url)
        url = sys.argv[0] + f"?action=list_items&category_url={encoded_category_url}"
        
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)
        print(f"DEBUG: '{category_name}' ক্যাটাগরি আইটেম যোগ করা হয়েছে। URL: {url}")

    xbmcplugin.endOfDirectory(addon_handle)
    print("DEBUG: প্রধান মেনু তৈরি সম্পন্ন হয়েছে।")

def list_items(current_xml_url):
    """নির্দিষ্ট XML ফাইল থেকে আইটেম (মুভি) অথবা সাব-ক্যাটাগরি লোড করে Kodi-এর ইন্টারফেসে দেখায়।"""
    print(f"DEBUG: আইটেম/সাব-ক্যাটাগরি তালিকা তৈরি করা হচ্ছে। বর্তমান XML URL: {current_xml_url}")
    
    root_element = fetch_xml_data(current_xml_url)
    if root_element is None:
        xbmcgui.Dialog().notification("Movie Club", "XML ফাইল লোড করা যায়নি। অনুগ্রহ করে লিঙ্কটি চেক করুন।", xbmcgui.NOTIFICATION_ERROR)
        print(f"ERROR: '{current_xml_url}' থেকে XML লোড হয়নি।")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
        return

    # প্রথমে মুভি/ভিডিও আইটেম খোঁজার চেষ্টা করুন
    items_to_display = root_element.findall('movie')
    if not items_to_display:
        items_to_display = root_element.findall('item')

    # যদি মুভি/ভিডিও আইটেম না পাওয়া যায়, তাহলে সাব-ক্যাটাগরি খোঁজার চেষ্টা করুন
    is_nested_category = False
    if not items_to_display:
        sub_categories = root_element.findall('category')
        if not sub_categories:
            sub_categories = root_element.findall('item') # যদি <item> সাব-ক্যাটাগরি হিসেবে ব্যবহার হয়
        
        if sub_categories:
            items_to_display = sub_categories
            is_nested_category = True
            print(f"DEBUG: '{current_xml_url}' এ নেস্টেড ক্যাটাগরি পাওয়া গেছে।")
        else:
            print(f"DEBUG: '{current_xml_url}' এ কোনো মুভি/আইটেম বা সাব-ক্যাটাগরি ট্যাগ পাওয়া যায়নি।")
            xbmcgui.Dialog().notification("Movie Club", "এই ফাইলে কোনো আইটেম বা সাব-ক্যাটাগরি পাওয়া যায়নি।", xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
            return

    # আইটেম বা সাব-ক্যাটাগরি ডিসপ্লে করুন
    for element in items_to_display:
        title = element.find('title').text if element.find('title') is not None else 'Unknown Title'
        link_url = element.find('link').text if element.find('link') is not None else None
        
        if not link_url:
            print(f"WARNING: '{title}' এর জন্য কোনো লিঙ্ক পাওয়া যায়নি, এড়িয়ে যাওয়া হচ্ছে।")
            continue

        list_item = xbmcgui.ListItem(label=title)
        
        # আর্টওয়ার্ক (thumb/thumbnail)
        thumb = element.find('thumbnail').text if element.find('thumbnail') is not None else None
        if not thumb:
            thumb = element.find('thumb').text if element.find('thumb') is not None else ADDON_ICON

        fanart = element.find('fanart').text if element.find('fanart') is not None else ADDON_FANART
        poster = element.find('poster').text if element.find('poster') is not None else thumb
        banner = element.find('banner').text if element.find('banner') is not None else poster
        clearart = element.find('clearart').text if element.find('clearart') is not None else fanart

        list_item.setArt({
            'thumb': thumb,
            'poster': poster,
            'fanart': fanart,
            'clearart': clearart,
            'banner': banner,
            'icon': thumb
        })

        if is_nested_category:
            # এটি একটি সাব-ক্যাটাগরি, ক্লিক করলে আরও আইটেম/সাব-ক্যাটাগরি লোড হবে
            encoded_next_url = urllib.parse.quote_plus(link_url)
            url_to_open = sys.argv[0] + f"?action=list_items&category_url={encoded_next_url}"
            is_folder = True
            print(f"DEBUG: সাব-ক্যাটাগরি যোগ করা হচ্ছে: {title}, URL: {url_to_open}")
        else:
            # এটি একটি প্লেয়েবল মুভি/আইটেম
            url_to_open = link_url
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
            
            year_str = element.find('year').text if element.find('year') is not None else ''
            genre_str = element.find('genre').text if element.find('genre') is not None else ''
            plot = element.find('plot').text if element.find('plot') is not None else ''

            try:
                year = int(year_str) if year_str and year_str.isdigit() else 0
            except ValueError:
                year = 0
                
            list_item.setInfo('video', {
                'title': title, 
                'year': year, 
                'genre': genre_str, 
                'plot': plot,
            })
            print(f"DEBUG: প্লেয়েবল আইটেম যোগ করা হচ্ছে: {title}, URL: {url_to_open}")

        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_to_open, listitem=list_item, isFolder=is_folder)

    xbmcplugin.endOfDirectory(addon_handle)
    print(f"DEBUG: মোট {len(items_to_display)} টি আইটেম/সাব-ক্যাটাগরি তালিকাভুক্ত করা হয়েছে।")


def router(paramstring):
    """URL প্যারামিটার হ্যান্ডেল করে এবং সঠিক ফাংশন কল করে।"""
    print(f"DEBUG: রাউটার শুরু হয়েছে। প্যারামিটার স্ট্রিং: {paramstring}")
    params = dict(urllib.parse.parse_qsl(paramstring)) 
    action = params.get('action') 

    if action == 'list_items':
        category_url = params.get('category_url')
        if category_url:
            list_items(current_xml_url=category_url) 
        else:
            xbmcgui.Dialog().notification("Movie Club", "কোন ক্যাটাগরি URL নির্দিষ্ট করা হয়নি।", xbmcgui.NOTIFICATION_ERROR)
            print("ERROR: 'list_items' অ্যাকশনের জন্য কোনো 'category_url' নির্দিষ্ট করা হয়নি।")
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False)
    else:
        build_menu()

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[2].startswith('?'):
        router(sys.argv[2][1:])
    else:
        build_menu()

