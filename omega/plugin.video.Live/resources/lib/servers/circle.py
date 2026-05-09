# -*- coding: utf-8 -*-
import random

# ্ডম কালার লিস্ট
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """কালার বেছে নেবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● English Movies (2016-26)[/B][/COLOR]" % get_clr(), "http://index2.circleftp.net/FILE/English%20%26%20Foreign%20Dubbed%20Movies/"),
    ("[COLOR %s][B]● English Movies (1995-15)[/B][/COLOR]" % get_clr(), "http://index.circleftp.net/FILE/English%20%26%20Foreign%20Dubbed%20Movies/"),
    ("[COLOR %s][B]● South Hindi Dubbed (2000-23)[/B][/COLOR]" % get_clr(), "http://ftp17.circleftp.net/FILE/Tamil%20Telugu%20%26%20Others%20Hindi%20Dubbed/"),
    ("[COLOR %s][B]● South Hindi Dubbed (2024-26)[/B][/COLOR]" % get_clr(), "http://ftp13.circleftp.net/FILE/Tamil%20Telugu%20%26%20Others%20Hindi%20Dubbed/"),
    ("[COLOR %s][B]● Hindi Movies[/B][/COLOR]" % get_clr(), "http://index1.circleftp.net/FILE/Hindi%20Movies/"),
    ("[COLOR %s][B]● Dubbed TV Series[/B][/COLOR]" % get_clr(), "http://ftp16.circleftp.net/FILE/Dubbed%20TV%20Series%20%26%20Shows/"),
]