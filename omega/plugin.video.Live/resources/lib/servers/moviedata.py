# -*- coding: utf-8 -*-
import random

# র্ডম কালার লিস্ট যা আপনার অ্যাডনটিকে চমৎকার লুক দেবে
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """লিস্ট থেকে একটিান্ডম কালার রিটার্ন করবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● English 1080p[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/English%20Movies%20(1080p)/"),
    ("[COLOR %s][B]● Hindi Movies[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/Hindi%20Movies/"),
    ("[COLOR %s][B]● South Dubbed[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/SOUTH%20INDIAN%20MOVIES/Hindi%20Dubbed/"),
    ("[COLOR %s][B]● IMDB Top 250[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/IMDb%20Top-250%20Movies/"),
    ("[COLOR %s][B]● Animation (1080p)[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/Animation%20Movies%20%281080p%29/"),
    ("[COLOR %s][B]● Animation Standard[/B][/COLOR]" % get_clr(), "http://10.1.1.1/data/Animation%20Movies/"),
]