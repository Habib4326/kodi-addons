# -*- coding: utf-8 -*-
import random

# র্ডম কালার লিস্ট যা কোডির ডার্ক থিমে উজ্জ্বল দেখাবে
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """লিস্ট থেকে একটিান্ডম কালার রিটার্ন করবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● Server S10[/B][/COLOR]" % get_clr(), "http://10.16.100.202/ftps10/"),
    ("[COLOR %s][B]● Server S3[/B][/COLOR]" % get_clr(), "http://10.16.100.206/ftps3/"),
    ("[COLOR %s][B]● Server S12[/B][/COLOR]" % get_clr(), "http://10.16.100.212/iccftps12/"),
    ("[COLOR %s][B]● Server S13[/B][/COLOR]" % get_clr(), "http://10.16.100.213/iccftps13/"),
    ("[COLOR %s][B]● Server S14[/B][/COLOR]" % get_clr(), "http://10.16.100.214/iccftps14/"),
]