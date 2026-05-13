import urllib.request
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui
import os
import json

from .utils import ADDON, safe

# মেইন মেনুর জন্য ক্যাশ
MOVIE_CACHE = {}

def load_categories():
    """
    এটি আপনার মেইন মেনু তৈরি করবে।
    """
    categories = [
        {"title": "Search", "type": "search"},
        {"title": "Movies By Year", "type": "years"},
        {"title": "All Movies (Main)", "type": "main_all"} # মেইন মুভির জন্য আলাদা টাইপ
    ]

    # ইউজারের অ্যাড করা কাস্টম ফাইলগুলো চেক করা
    user_xml_data = ADDON.getSetting('xml_list')
    if user_xml_data:
        try:
            added_files = json.loads(user_xml_data)
            for file_info in added_files:
                name = file_info.get('name', 'Custom File')
                path = file_info.get('path')
                if path:
                    # প্রতিটি ফাইলকে আলাদা ক্যাটাগরি হিসেবে যোগ করা
                    categories.append({
                        "title": name, 
                        "type": "custom_single", 
                        "path": path
                    })
        except:
            pass

    return categories

def load_movies(mode="main_all", custom_path=None):
    """
    মুভি লোড করার মেইন ফাংশন।
    এটি মোড অনুযায়ী মেইন অথবা কাস্টম ফাইল থেকে ডাটা আনে।
    """
    global MOVIE_CACHE
    
    # ক্যাশ কী তৈরি করা (যাতে একটার ডাটা অন্যটায় না মেশে)
    cache_key = custom_path if custom_path else mode
    
    if cache_key in MOVIE_CACHE:
        return MOVIE_CACHE[cache_key]

    movie_list = []

    # ১. মেইন মুভি লোড করা (All Movies Main)
    if mode == "main_all":
        main_url = ADDON.getSetting('xml_url')
        if not main_url:
            main_url = "https://raw.githubusercontent.com/Habib4326/ICC_Live_posterxml/main/movie_database.xml"
        movie_list = fetch_xml_data(main_url)

    # ২. কাস্টম ফাইল লোড করা (যেমন: Brazzers)
    elif mode == "custom_single" and custom_path:
        movie_list = fetch_xml_data(custom_path)

    # ৩. যদি মেইন লিস্টে কিছু না পায়, তবে ব্যাকআপ হিসেবে কাস্টম ফাইলগুলো চেক করা
    if not movie_list and mode == "main_all":
        xbmc.log("Main URL failed, checking for general list...", xbmc.LOGINFO)

    MOVIE_CACHE[cache_key] = movie_list
    return movie_list

def fetch_xml_data(url_or_path):
    """URL বা লোকাল পাথ থেকে XML ডাটা সংগ্রহের লজিক"""
    temp_list = []
    if not url_or_path:
        return temp_list

    try:
        if url_or_path.startswith('http'):
            # অনলাইন URL-এর জন্য হেডার যোগ করা হয়েছে যাতে ব্লক না করে
            req = urllib.request.Request(url_or_path, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            xml_data = response.read()
        else:
            # লোকাল ফাইলের জন্য
            with open(url_or_path, 'r', encoding='utf-8') as f:
                xml_data = f.read()

        root = ET.fromstring(xml_data)
        for movie in root.findall("movie"):
            temp_list.append(parse_movie_node(movie))
    except Exception as e:
        xbmc.log(f"Error loading XML from {url_or_path}: {str(e)}", xbmc.LOGERROR)
    
    return temp_list

def parse_movie_node(movie):
    """মুভি নোড থেকে ডাটা রিড করা"""
    return {
        "title": safe(movie.findtext("title", "Unknown")),
        "year": str(movie.findtext("year", "0")).strip(),
        "link": movie.findtext("link", ""),
        "poster": movie.findtext("poster", ""),
        "fanart": movie.findtext("fanart", ""),
        "rating": movie.findtext("rating", "N/A")
    }