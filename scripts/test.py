import requests as http
from bs4 import BeautifulSoup

from bible_extractor.bible import *

urls = [
        "http://www.drbo.org/",
        "http://biblehub.com/kj2000/",
        ]

def get_html(url):
    return BeautifulSoup(http.get(url).text, "html5lib")
