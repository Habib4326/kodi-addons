# -*- coding: utf-8 -*-

import sys
import os
import threading
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests

from bs4 import BeautifulSoup

import utils
from downloader import HtmlDownloader


# ============================================
# KODI HANDLE & ADDON SETTINGS
# ============================================

HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon()


# ============================================
# MAIN MENU
# ============================================

def show_main_menu():

    # Latest Updates
    utils.add_directory_item(
        HANDLE,
        "Latest Updates",
        "show_pages",
        "latest-updates"
    )

    # Top Rated
    utils.add_directory_item(
        HANDLE,
        "Top Rated",
        "show_pages",
        "top-rated"
    )

    # Most Popular
    utils.add_directory_item(
        HANDLE,
        "Most Popular",
        "show_pages",
        "most-popular"
    )

    # Categories
    utils.add_directory_item(
        HANDLE,
        "Categories",
        "show_categories",
        "https://pornky.st/categories/"
    )

    xbmcplugin.endOfDirectory(HANDLE)


# ============================================
# SHOW PAGES
# ============================================

def show_pages(category):

    downloader = HtmlDownloader()

    # প্রথম পেজ লোড
    first_page_url = f"https://pornky.st/{category}/"

    html_content = downloader.fetch_html(
        first_page_url
    )

    if not html_content:

        xbmcgui.Dialog().notification(
            "Error",
            "Failed to load pages.",
            xbmcgui.NOTIFICATION_ERROR,
            4000
        )

        return

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    # ডিফল্ট
    max_pages = 1

    try:

        page_links = soup.select("a[href]")

        for link in page_links:

            href = link.get("href", "")

            if f"/{category}/" in href:

                parts = href.strip("/").split("/")

                if parts[-1].isdigit():

                    page_num = int(parts[-1])

                    if page_num > max_pages:
                        max_pages = page_num

    except Exception as e:

        xbmc.log(
            f"[HabibMedia] Pagination Error: {e}",
            xbmc.LOGERROR
        )

    # PAGE CREATE
    for page in range(1, max_pages + 1):

        if page == 1:
            url = f"https://pornky.st/{category}/"
        else:
            url = f"https://pornky.st/{category}/{page}/"

        utils.add_directory_item(
            HANDLE,
            f"Page {page}",
            "fetch_movies",
            url
        )

    xbmcplugin.endOfDirectory(HANDLE)


# ============================================
# SHOW CATEGORIES
# ============================================

def show_categories(url):

    downloader = HtmlDownloader()

    html_content = downloader.fetch_html(url)

    if not html_content:

        xbmcgui.Dialog().notification(
            "Error",
            "Failed to load categories.",
            xbmcgui.NOTIFICATION_ERROR,
            4000
        )

        return

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    added = set()

    # CATEGORY LINKS
    category_links = soup.select(
        'a[href*="/categories/"]'
    )

    for link in category_links:

        try:

            href = link.get(
                "href",
                ""
            ).strip()

            title = link.get_text(
                strip=True
            )

            # empty title skip
            if not title:
                continue

            # only category links
            if "/categories/" not in href:
                continue

            # duplicate skip
            if href in added:
                continue

            added.add(href)

            utils.add_directory_item(
                HANDLE,
                title,
                "fetch_movies",
                href
            )

        except Exception as e:

            xbmc.log(
                f"[HabibMedia] Category Error: {e}",
                xbmc.LOGERROR
            )

    xbmcplugin.endOfDirectory(HANDLE)
    

# ============================================
# MOVIE LIST (UPDATED TO PASS TITLE TO ROUTER)
# ============================================

def list_movies(url):

    downloader = HtmlDownloader()

    html_content = downloader.fetch_html(url)

    if not html_content:

        xbmcgui.Dialog().notification(
            "Error",
            "Failed to scrape page list.",
            xbmcgui.NOTIFICATION_ERROR,
            4000
        )

        return

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    items = soup.select("div.video")

    for item in items:

        try:

            a = item.select_one("a[href]")
            img = item.select_one("img")

            if not a:
                continue

            href = a.get(
                "href",
                ""
            ).strip()

            title = (
                img.get("alt")
                or img.get("title")
                or a.get_text(strip=True)
                or "Untitled"
            ).strip()

            poster = (
                img.get("src")
                or img.get("data-src")
                or ""
            ).strip()

            if poster.startswith("/"):
                poster = (
                    "https://pornky.st"
                    + poster
                )

            # এখানে টাইটেল প্যারামিটারটি যুক্ত করা হলো যাতে প্লে করার সময় টাইটেল পাওয়া যায়
            play_url = f"{href}&title={requests.utils.quote(title)}"

            utils.add_directory_item(
                HANDLE,
                title,
                "play_video",
                url=play_url,
                poster=poster,
                is_folder=False
            )

        except Exception as e:

            xbmc.log(
                f"[HabibMedia] Item Parse Error: {e}",
                xbmc.LOGERROR
            )

    xbmcplugin.endOfDirectory(HANDLE)


# ============================================
# TERMUX API STREAM RESOLVER
# ============================================

def resolve_stream_from_api(page_url):

    try:

        xbmc.log(
            "[HabibMedia] Connecting to Termux API...",
            xbmc.LOGINFO
        )

        response = requests.get(
            "http://127.0.0.1:8080/resolve",
            params={
                "url": page_url
            },
            timeout=120
        )

        xbmc.log(
            f"[HabibMedia] Status Code: {response.status_code}",
            xbmc.LOGINFO
        )

        if response.status_code != 200:
            return None

        data = response.json()

        stream_url = data.get(
            "stream_url"
        )

        xbmc.log(
            f"[HabibMedia] STREAM URL: {stream_url}",
            xbmc.LOGINFO
        )

        if stream_url:
            return stream_url

        return None

    except Exception as e:

        xbmc.log(
            f"[HabibMedia] API Error: {e}",
            xbmc.LOGERROR
        )

        return None


# ============================================
# BACKGROUND DOWNLOADER FUNCTION (UPDATED WITH TITLE)
# ============================================

def download_file(stream_url, download_path, video_title):
    try:
        # ফাইলের নাম থেকে অবৈধ উইন্ডোজ/অ্যান্ড্রয়েড ক্যারেক্টার বাদ দেওয়া (Clean Filename)
        clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_', '-', '.')]).strip()
        clean_title = clean_title.replace(' ', '_') # স্পেসের বদলে আন্ডারস্কোর ব্যবহার
        
        if not clean_title:
            clean_title = "HabibMedia_Video"

        # সঠিক এক্সটেনশন নির্ধারণ করা
        ext = ".mp4"
        if ".mkv" in stream_url:
            ext = ".mkv"
            
        filename = f"{clean_title}{ext}"
        full_path = os.path.join(download_path, filename)

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
            "Referer": "https://pornky.st/"
        }

        xbmc.log(f"[HabibMedia] Background worker thread active. Downloading: {filename} to {download_path}", xbmc.LOGINFO)

        # স্ট্রিম আকারে ডাউনলোড শুরু
        response = requests.get(stream_url, headers=headers, stream=True, timeout=60)
        if response.status_code == 200:
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
            
            # ডাউনলোড সফল হওয়ার মেসেজ
            xbmcgui.Dialog().notification(
                "Download Complete",
                f"Saved: {filename}",
                xbmcgui.NOTIFICATION_INFO,
                5000
            )
        else:
            raise Exception(f"HTTP Server error code: {response.status_code}")

    except Exception as e:
        xbmc.log(f"[HabibMedia] Worker Download Failed: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok("Download Failed", f"Error encountered:\n{str(e)}")


# ============================================
# PLAY VIDEO & DOWNLOAD CHECK (UPDATED WITH TITLE)
# ============================================

def play_video(combined_url):

    # ইউআরএল থেকে আসল পেজ ইউআরএল এবং ভিডিওর টাইটেল আলাদা করা
    page_url = combined_url
    video_title = "HabibMedia_Video"
    
    if "&title=" in combined_url:
        parts = combined_url.split("&title=")
        page_url = parts[0]
        video_title = requests.utils.unquote(parts[1])

    p_dialog = xbmcgui.DialogProgress()

    p_dialog.create(
        "Habib Media",
        "Capturing protected stream..."
    )

    try:

        stream_url = resolve_stream_from_api(
            page_url
        )

        p_dialog.close()

        if stream_url:

            # ----------------------------------------------------
            # সেটিংসে ডাউনলোড অপশন চালু আছে কিনা চেক করার লজিক
            # ----------------------------------------------------
            is_download_enabled = ADDON.getSettingBool('enable_download')
            download_path = ADDON.getSetting('download_path')

            if is_download_enabled and download_path:
                choice = xbmcgui.Dialog().yesno(
                    "HabibMedia Options",
                    f"Do you want to download this video?\n\nTitle: {video_title}",
                    yeslabel="Download",
                    nolabel="Play Only"
                )
                
                if choice:
                    # ডাউনলোড শুরুর পপআপ প্রম্পট
                    xbmcgui.Dialog().notification(
                        "Download Started", 
                        f"Downloading: {video_title}",
                        xbmcgui.NOTIFICATION_INFO,
                        4000
                    )
                    
                    # কোডি প্লেব্যাক ইঞ্জিনকে ডামি রেসপন্স দিয়ে শান্ত করা
                    dummy_item = xbmcgui.ListItem(path=stream_url)
                    dummy_item.setProperty("IsPlayable", "false")
                    xbmcplugin.setResolvedUrl(HANDLE, True, listitem=dummy_item)
                    
                    # ব্যাকগ্রাউন্ড থ্রেডে টাইটেলসহ ডাউনলোড শুরু করা
                    downloader_thread = threading.Thread(target=download_file, args=(stream_url, download_path, video_title))
                    downloader_thread.start()
                    return

            # ----------------------------------------------------
            # ভিডিও প্লে করার নিয়মিত অংশ
            # ----------------------------------------------------
            headers = (
                "User-Agent=Mozilla/5.0%20"
                "(Linux;%20Android%2013)"
                "&Referer=https://pornky.st/"
            )

            kodi_playable_url = (
                f"{stream_url}|{headers}"
            )

            xbmc.log(
                f"[HabibMedia] PLAY URL: {kodi_playable_url}",
                xbmc.LOGINFO
            )

            list_item = xbmcgui.ListItem(
                path=kodi_playable_url
            )

            # PLAYABLE
            list_item.setProperty(
                "IsPlayable",
                "true"
            )

            # MP4
            if ".mp4" in stream_url:

                list_item.setMimeType(
                    "video/mp4"
                )

            # HLS
            elif ".m3u8" in stream_url:

                list_item.setMimeType(
                    "application/vnd.apple.mpegurl"
                )

                list_item.setProperty(
                    "inputstream",
                    "inputstream.ffmpegdirect"
                )

            xbmcplugin.setResolvedUrl(
                HANDLE,
                True,
                listitem=list_item
            )

        else:

            xbmcplugin.setResolvedUrl(
                HANDLE,
                False,
                listitem=xbmcgui.ListItem()
            )

            xbmcgui.Dialog().ok(
                "Failed",
                "Could not resolve stream URL.\n\n"
                "Make sure Hugging Face Cloud Space is running."
            )

    except Exception as e:

        p_dialog.close()

        xbmc.log(
            f"[HabibMedia] Playback Error: {e}",
            xbmc.LOGERROR
        )

        xbmcplugin.setResolvedUrl(
            HANDLE,
            False,
            listitem=xbmcgui.ListItem()
        )

        xbmcgui.Dialog().ok(
            "Playback Error",
            str(e)
        )


# ============================================
# ROUTER
# ============================================

if __name__ == '__main__':

    params = utils.get_args()

    mode = params.get("mode")

    if not mode:

        show_main_menu()

    elif mode == "show_pages":

        show_pages(
            params.get("url")
        )

    elif mode == "show_categories":

        show_categories(
            params.get("url")
        )

    elif mode == "fetch_movies":

        list_movies(
            params.get("url")
        )

    elif mode == "play_video":

        play_video(
            params.get("url")
        )