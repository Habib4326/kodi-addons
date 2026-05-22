# -*- coding: utf-8 -*-

import requests
import xbmc


class HeadlessBrowser:

    def __init__(self):
        # আপনার Hugging Face এর সঠিক পাবলিক লিংক
        self.api_url = "https://habib4326-habib-resolver.hf.space/resolve"

    def resolve_stream_url(self, page_url):
        try:
            xbmc.log(
                "[HabibMedia] Connecting to Cloud Resolver...",
                xbmc.LOGINFO
            )

            # সার্ভারকে বোকা বানানোর জন্য ব্রাউজার হেডার যুক্ত করা হলো
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }

            response = requests.get(
                self.api_url,
                params={
                    "url": page_url
                },
                headers=headers, # এখানে হেডারটি যুক্ত করা হয়েছে
                timeout=120
            )

            xbmc.log(
                f"[HabibMedia] HTTP Status: {response.status_code}",
                xbmc.LOGINFO
            )

            if response.status_code != 200:
                xbmc.log(
                    "[HabibMedia] Bad HTTP response",
                    xbmc.LOGERROR
                )
                return None

            data = response.json()

            xbmc.log(
                f"[HabibMedia] API Response: {data}",
                xbmc.LOGINFO
            )

            status = data.get("status")

            if status != "success":
                xbmc.log(
                    "[HabibMedia] Resolver failed",
                    xbmc.LOGERROR
                )
                return None

            stream_url = data.get("stream_url")

            if not stream_url:
                xbmc.log(
                    "[HabibMedia] No stream URL returned",
                    xbmc.LOGERROR
                )
                return None

            xbmc.log(
                f"[HabibMedia] Stream Found: {stream_url}",
                xbmc.LOGINFO
            )

            return stream_url

        except requests.exceptions.Timeout:
            xbmc.log(
                "[HabibMedia] Resolver timeout",
                xbmc.LOGERROR
            )
            return None

        except Exception as e:
            xbmc.log(
                f"[HabibMedia] API Error: {e}",
                xbmc.LOGERROR
            )
            return None