# -*- coding: utf-8 -*-
import random

# র্ডম কালার লিস্ট যা কোডির ডার্ক থিমে উজ্জ্বল দেখাবে
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """লিস্ট থেকে একটিান্ডম কালার রিটার্ন করবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● Web Series[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/KOREAN%20TV%20%26%20WEB%20Series/"),
]