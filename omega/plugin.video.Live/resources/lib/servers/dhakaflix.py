# -*- coding: utf-8 -*-
import random

# র্যান্ডম কালার লিস্ট যা আপনার ইন্টারফেসে সুন্দর দেখাবে
COLORS = ["gold", "deepskyblue", "lime", "orange", "magenta", "cyan", "yellow", "red", "chartreuse"]

def get_clr():
    """লিস্ট থেকোন্ডম কালার রিটার্ন করবে"""
    return random.choice(COLORS)

SERVERS = [
    ("[COLOR %s][B]● English (1080p)[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/English%20Movies%20%281080p%29/"),
    
    ("[COLOR %s][B]● English Standard[/B][/COLOR]" % get_clr(), "http://172.16.50.7/DHAKA-FLIX-7/English%20Movies/"),
    
    ("[COLOR %s][B]● Hindi Movies[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/Hindi%20Movies/"),
    
    ("[COLOR %s][B]● South Dubbed[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/SOUTH%20INDIAN%20MOVIES/Hindi%20Dubbed/"),
    ("[COLOR %s][B]● Kolkata Bangla[/B][/COLOR]" % get_clr(), "http://172.16.50.7/DHAKA-FLIX-7/Kolkata%20Bangla%20Movies/"),
    
    ("[COLOR %s][B]● Animation Movies[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/Animation%20Movies/"),
    
     ("[COLOR %s][B]● Animation Movies-1080[/B][/COLOR]" % get_clr(), "http://172.16.50.14/DHAKA-FLIX-14/Animation%20Movies%20%281080p%29/"),
    
    ("[COLOR %s][B]● Foreign Language[/B][/COLOR]" % get_clr(), "http://172.16.50.7/DHAKA-FLIX-7/Foreign%20Language%20Movies/"),
]