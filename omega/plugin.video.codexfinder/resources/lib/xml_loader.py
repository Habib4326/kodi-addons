import urllib.request
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui
import os
import json # JSON সাপোর্ট যোগ করা হয়েছে

from .utils import ADDON, safe

# মেইন মেনুর মুভিগুলো জমা রাখার জন্য ক্যাশ
MOVIE_CACHE = None

def load_movies(custom_path=None):
    """
    মুভি লোড করার মেইন ফাংশন। 
    যদি custom_path দেওয়া হয়, তবে শুধু সেই নির্দিষ্ট পাথ থেকে লোড করবে।
    অন্যথায় মেইন URL এবং কাস্টম অ্যাড করা সব ফাইল একসাথে লোড করবে।
    """
    global MOVIE_CACHE

    # ১. যদি নির্দিষ্ট কোনো ডিরেক্টরি থেকে লোড করতে বলা হয় (কাস্টম ফোল্ডার)
    if custom_path:
        return fetch_xml_data(custom_path)

    # ২. মেইন মেনুর জন্য যদি আগে থেকেই ডাটা লোড করা থাকে (Cache)
    if MOVIE_CACHE:
        return MOVIE_CACHE

    movie_list = []

    # ৩. সেটিংস থেকে মেইন XML URL নেওয়া
    main_url = ADDON.getSetting('xml_url')
    if not main_url:
        # সেটিংস খালি থাকলে ডিফল্ট গিটহাব লিঙ্ক ব্যবহার হবে
        main_url = "https://raw.githubusercontent.com/Habib4326/ICC_Live_posterxml/main/movie_database.xml"
    
    # মেইন মুভিগুলো লিস্টে যোগ করা
    movie_list.extend(fetch_xml_data(main_url))

    # ৪. ইউজারের অ্যাড করা অতিরিক্ত XML ফাইলগুলো (xml_list) লোড করা
    user_xml_data = ADDON.getSetting('xml_list')
    
    if user_xml_data:
        try:
            added_files = json.loads(user_xml_data)
            for file_info in added_files:
                path = file_info.get('path')
                if path:
                    # মেইন লিস্টের সাথে কাস্টম ফাইলগুলোর মুভিও মিশিয়ে দেওয়া
                    movie_list.extend(fetch_xml_data(path))
        except Exception as e:
            xbmc.log(f"JSON Parse Error in xml_loader: {str(e)}", xbmc.LOGERROR)

    # মেইন মেনুর জন্য রেজাল্ট ক্যাশ করা
    MOVIE_CACHE = movie_list
    return movie_list

def fetch_xml_data(url_or_path):
    """URL বা লোকাল পাথ থেকে XML ডেটা ফেচ করার কমন লজিক"""
    temp_list = []
    if not url_or_path:
        return temp_list

    try:
        if url_or_path.startswith('http'):
            # অনলাইন URL থেকে লোড
            response = urllib.request.urlopen(url_or_path)
            xml_data = response.read()
        else:
            # লোকাল স্টোরেজ থেকে ফাইল লোড
            with open(url_or_path, 'r', encoding='utf-8') as f:
                xml_data = f.read()

        root = ET.fromstring(xml_data)
        for movie in root.findall("movie"):
            temp_list.append(parse_movie_node(movie))
    except Exception as e:
        xbmc.log(f"Error loading XML from {url_or_path}: {str(e)}", xbmc.LOGERROR)
    
    return temp_list

def parse_movie_node(movie):
    """একটি মুভি নোড থেকে ডাটা এক্সট্রাক্ট করার কমন ফাংশন"""
    return {
        "title": safe(movie.findtext("title", "Unknown")),
        "year": str(movie.findtext("year", "0")).strip(),
        "link": movie.findtext("link", ""),
        "poster": movie.findtext("poster", ""),
        "fanart": movie.findtext("fanart", ""),
        "rating": movie.findtext("rating", "N/A")
    }