from resources.lib.adultsite import AdultSite
from resources.lib import utils
import re

# সাইটের পরিচিতি সেটআপ
site = AdultSite('pornhubnew', "[COLOR orange]PornHubnew[/COLOR]", 'https://www.pornhub.com/', 'icon.png', 'pornhub')

@site.register(default_mode=True)
def Main():
    # হোমপেজ মেনু তৈরি
    site.add_dir('Most Recent', site.url + 'video?o=mr', 'List', site.img_search)
    site.add_dir('Top Rated', site.url + 'video?o=tr', 'List', site.img_search)
    utils.eod()

@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    # এখানে আপনাকে HTML বিশ্লেষণ করতে হবে
    # ডিলিমিটার এবং রেজেক্স (Regex) সেট করুন
    # ...
    utils.videos_list(site, 'pornhub.Playvid', html, delimiter, re_videopage, re_name, re_img)
    utils.eod()

@site.register()
def Playvid(url, name):
    # ভিডিও প্লে করার লজিক
    # ...