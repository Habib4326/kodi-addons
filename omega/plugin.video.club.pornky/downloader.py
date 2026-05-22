import requests

class HtmlDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A325F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }
        self.cookies = {
            "device_verified": "true",
            "kt_referer": "https://www.google.com/",
            "PHPSESSID": "ffqtcagcbl1frr47v07kqk3if7"
        }

    def fetch_html(self, url):
        try:
            response = self.session.get(url, headers=self.headers, cookies=self.cookies, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            pass
        return None