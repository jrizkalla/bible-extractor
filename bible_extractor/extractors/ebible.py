import logging
import re
from collections import OrderedDict

import requests as http
from bs4 import BeautifulSoup

from ..extract import extractor, Url
from ..bible import Bible, Verse, Testament

@extractor("http://ebible.org/eng-lxx2012/")
def ebible_extractor(url: Url) -> Bible:
    log = logging.getLogger(__name__)
    bible = Bible(name="Septuagint in American English")
    
    info = http.get("http://ebible.org/study/content/texts/ENGLXX/info.json").json()
    sections = OrderedDict([ (
        division,
        [ sec for sec in info["sections"] if sec.startswith(info["divisions"][i]) ]
        ) for i, division in enumerate(info["divisionNames"])
        ])
    
    num_chapters = sum(len(chap) for chap in sections.values())

    SECTION_URL = "http://ebible.org/study/content/texts/ENGLXX/{}.html"
    
    VERSE_CLS_REGEX = re.compile("v-(\d+)(-\d+)?")
    # download and parse the sections
    # make the bible
    EXTRACT_NUM_REGEX = re.compile(r"^[^\d]*(\d+)$")
    chap_count = -1
    for book, chapters in sections.items():
        for chap_code in chapters:
            chap_count += 1
            log.info(f"({chap_count*100 // num_chapters:3}%) Extracting chapter {chap_code} in {book}")
            # get the chapter number
            try:
                chap_num = int(EXTRACT_NUM_REGEX.match(chap_code).group(1))
            except (AttributeError, ValueError):
                book.warn(Verse.Loc(book, -1, -1), 
                        f"Unknown chapter number. Chapter code is {chap_code}")
                continue
            
            chap_page = BeautifulSoup(
                    http.get(SECTION_URL.format(chap_code)).text, "html5lib")
            for verse_html in chap_page.find_all(class_="v-num"):
                verse_matches = (VERSE_CLS_REGEX.fullmatch(cls) 
                        for cls in verse_html.attrs["class"])
                try:
                    verse_match = next(vm for vm in verse_matches if vm) # first match
                except StopIteration:
                    bible.warn(Verse.Loc(book, chap_num, -1), "Cannot find verses")
                    continue
                try:
                    verse_num = int(verse_match.group(1))
                except (AttributeError, ValueError):
                    bible.warn(Verse.Loc(book, chap_num, -1), "Cannot find verse number")
                    continue
                
                parent = verse_html.parent
                verse = parent.text[len(parent.find_next().text):].strip()
                if verse_match.group(2):
                    # More than one verse
                    locs = [
                            Verse.Loc(book, verse_num, v)
                            for v in range(verse_num, int(verse_match.group(2)[1:])+1)
                            ]
                    bible.warn(locs, "Found bible range. Merging into the first verse.")
                
                bible += Verse(Verse.Loc(book, chap_num, verse_num, Testament.old), verse)
    return bible
