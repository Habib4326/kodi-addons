import urllib.request
import xml.etree.ElementTree as ET
import xbmc
import xbmcgui
import os

from .utils import ADDON, safe

# মেইন মেনুর জন্য ক্যাশ
MOVIE_CACHE = {}

# ডিফল্ট এক্সএমএল লিঙ্ক
DEFAULT_XML_URL = "https://raw.githubusercontent.com/Habib4326/ICC_Live_posterxml/main/movie_database.xml"

def load_categories():
    """
    এটি আপনার মেইন মেনু তৈরি করবে।
    """
    categories = [
        {"title": "Search", "type": "search"},
        {"title": "Movies By Year", "type": "years"},
        {"title": "All Movies (Main)", "type": "main_all"}
    ]
    return categories

def load_movies():
    """
    মুভি লোড করার মেইন ফাংশন।
    এটি সরাসরি নির্দিষ্ট ডিফল্ট URL থেকে ডাটা আনে।
    """
    global MOVIE_CACHE
    
    cache_key = "main_all"
    
    if cache_key in MOVIE_CACHE:
        return MOVIE_CACHE[cache_key]

    # সরাসরি ডিফল্ট লিঙ্ক থেকে মুভি লিস্ট সংগ্রহ করা হচ্ছে
    movie_list = fetch_xml_data(DEFAULT_XML_URL)

    MOVIE_CACHE[cache_key] = movie_list
    return movie_list

def search_movies(query):
    """
    ইউজারের দেওয়া কিওয়ার্ড দিয়ে মুভি ডাটাবেজে সার্চ করার ফাংশন।
    """
    if not query:
        return []
        
    all_movies = load_movies()
    # মুভির টাইটেল লোয়ারকেস করে সার্চ কিওয়ার্ডের সাথে মেলানো হচ্ছে
    filtered_movies = [m for m in all_movies if query.lower() in m.get('title', '').lower()]
    return filtered_movies

def fetch_xml_data(url):
    """URL থেকে XML ডাটা সংগ্রহের লজিক"""
    temp_list = []
    if not url:
        return temp_list

    try:
        # অনলাইন URL-এর জন্য হেডার যোগ করা হয়েছে যাতে ব্লক না করে
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()

        root = ET.fromstring(xml_data)
        for movie in root.findall("movie"):
            temp_list.append(parse_movie_node(movie))
    except Exception as e:
        xbmc.log(f"Error loading XML from {url}: {str(e)}", xbmc.LOGERROR)
    
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