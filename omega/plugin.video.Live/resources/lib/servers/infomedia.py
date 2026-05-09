# -*- coding: utf-8 -*-
import random

# র্ডম কালার লিস্ট যা কোডির ডার্ক থিমে উজ্জ্বল দেখাবে
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """লিস্ট থেকে একটিান্ডম কালার রিটার্ন করবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● HDD - 01[/B][/COLOR]" % get_clr(), "http://103.225.94.27/Infobase/hdd-1/"),
    ("[COLOR %s][B]● HDD - 02[/B][/COLOR]" % get_clr(), "http://103.225.94.27/Infobase/hdd-2/"),
    ("[COLOR %s][B]● HDD - 03[/B][/COLOR]" % get_clr(), "http://103.225.94.27/Infobase/hdd-3/"),
    ("[COLOR %s][B]● HDD - 04[/B][/COLOR]" % get_clr(), "http://103.225.94.27/Infobase/hdd-4/"),
    ("[COLOR %s][B]● HDD - 05[/B][/COLOR]" % get_clr(), "http://103.225.94.27/Infobase/hdd-5/"),
]