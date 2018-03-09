import logging
import re
from urllib.parse import urljoin
from collections import OrderedDict

import requests as http
from bs4 import BeautifulSoup

from ..extract import extractor, Url
from ..bible import Bible, Verse, Testament
from ..progress import ProgressIndicator
from .. import warnings as warn

# unfortunately, for this source, book names must be hard coded
NEW_TEST_NAMES = set() # placeholder
ABREVS = {} # placeholder

class URLS:
    books = "http://biblehub.com/menus/versemenus/genesisbookmenu.htm"
    
    @classmethod
    def chapters(cls, book_name):
        url_book_name = book_name.lower().replace(" ", "_") + "/"
        return urljoin(
                urljoin("http://biblehub.com/kj2000/cmenus/", url_book_name),
                "1.htm")
    

@extractor("http://biblehub.com/kj2000/")
def biblehub(url: Url) -> Bible:
    log = ProgressIndicator(logging.getLogger(__name__))
    bible = Bible(name="King James 2000")
    
    # get the book names
    book_names_page = BeautifulSoup(http.get(URLS.books).text, "html5lib")
    book_names = [ ABBREVS.get(opt.text, opt.text) 
            for opt in book_names_page.find_all("option") ]
    del book_names_page
    
    # find the chapters
    chapters = { Testament.old : {}, Testament.new : {} }
    total_num_chapters = 0
    for book_name in book_names:
        # get the chapters
        chap_list_page = BeautifulSoup(http.get(URLS.chapters(book_name)).text,
                "html5lib")
        num_chapters = len(chap_list_page.select("select[name=select2] > option"))
        if num_chapters <= 0:
            bible.warn(Verse.Loc(book_name, -1, -1, -1),
                    f"Number of chapters is {num_chapters}")
            
        test = Testament.new if book_name in NEW_TEST_NAMES else Testament.old
        chapters[test][book_name] = num_chapters
        total_num_chapters += num_chapters
    
    log.num_chapters = total_num_chapters
    total_chap_idx = -1
    
    for test in (Testament.old, Testament.new):
        for book_name, num_chapters in chapters[test].items():
            # download the chapter
            for chap_num in range(1, num_chapters+1):
                total_chap_idx += 1
                log.starting(total_chap_idx, f"Processing chapter {chap_num} in {book_name}")
                chap_url = urljoin(url, 
                        book_name.lower().replace(" ", "_") 
                        + "/" + str(chap_num) + ".htm")
                chap_page = BeautifulSoup(http.get(chap_url).text, "html5lib")
                for verse in chap_page.select("div.chap > p.regular"):
                    try:
                        verse_num_str = verse.find("span", class_="reftext").text
                    except AttributeError:
                        bible.warn(Verse.Loc(book_name, chap_num, -1, test),
                                f"Unable to find verse number", 
                                warn.cannot_find_verse_num)
                        continue
                        
                    try:
                        verse_num = int(verse_num_str)
                    except ValueError:
                        bible.warn(Verse.Loc(book_name, chap_num, -1, test),
                                f"Unable to parse verse number '{verse_num_str}'",
                                warn.unknown_verse_num)
                        continue
                    
                    verse_spans = verse.find_all(lambda e:
                            e.name == "span" 
                            and "reftext" not in e.attrs.get("class", []))
                    verse_text = "\n".join(e.text for e in verse_spans)
                    
                    bible += Verse(Verse.Loc(book_name, chap_num, verse_num, test),
                            verse_text)
    return bible
    
    
    
    
    
# HARDCODED new testament names
NEW_TEST_NAMES = set(
"""Matthew
Mark
Luke
John
Acts
Romans
1 Corinthians
2 Corinthians
Galatians
Ephesians
Philippians
Colossians
1 Thessalonians
2 Thessalonians
1 Timothy
2 Timothy
Titus
Philemon
Hebrews
James
1 Peter
2 Peter
1 John
2 John
3 John
Jude
Revelation""".split("\n"))

ABBREVS = {
        "1 Thessalon.": "1 Thessalonians",
        "2 Thessalon.": "2 Thessalonians",
        }
