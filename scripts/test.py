import requests as http
from bs4 import BeautifulSoup

from bible_extractor.bible import *

urls = [
        "http://www.drbo.org/"
        ]

def get_html(url):
    return BeautifulSoup(http.get(url).text, "html5lib")
