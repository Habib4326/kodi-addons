import re
import urllib.parse

class TrafficFilter:
    @staticmethod
    def extract_clean_links(request_url):
        """ইউআরএল ফিল্টার করে আসল ভিডিও লিংক বের করে।"""
        decoded_url = urllib.parse.unquote(request_url)
        matches = re.findall(r'(https?://[^\s"\']+\.(?:mp4|m3u8)[^\s?&"\']*)', decoded_url, re.IGNORECASE)
        
        valid_links = []
        for match in matches:
            if not any(x in match for x in ["ping.gif", "get_image", "poster", "analytics", "favicon"]):
                valid_links.append(match)
        return valid_links