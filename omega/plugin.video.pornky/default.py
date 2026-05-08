# -*- coding: utf-8 -*-

import sys

from resources.lib.router import router
from resources.lib.menu import build_menu


if __name__ == '__main__':

    if len(sys.argv) > 2 and sys.argv[2]:

        router(sys.argv[2][1:])

    else:

        build_menu()