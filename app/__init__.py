class Login:
    def __init__(self):
        pass

    def show(self):
        print("Login page")
# This file makes "app" a Python package.
# It also exposes schema functions so they can be imported cleanly.

from .schema import create_all_tables
