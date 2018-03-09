"""
Provides functions to extract the data from websites.
"""
from typing import NewType, Callable, no_type_check
from collections import OrderedDict
from urllib.parse import urljoin
import re

import logging
log = logging.getLogger(__name__)

import requests as http
from bs4 import BeautifulSoup

from .bible import *

Url = NewType("Url", str)
ExtractorFunc = Callable[[Url], None]

class Extractor:
    """
    Manages a list of extractors for specific websites.
    """
    
    def __init__(self) -> None:
        self.extractors: OrderedDict[Url, ExtractorFunc] = OrderedDict()
    
    def register_extractor(self, url: Url, func: ExtractorFunc) -> None:
        """
        Register func as an extractor for url.
        """
        self.extractors[url] = func
    
    @no_type_check
    def extractor(self, url):
        """
        Decorator version of register_extractor
        """
        def _extractor(func):
            self.extractors[url] = func
            return func
        return _extractor

    def extract(self, url: Url) -> Bible:
        """
        Extract from a url.
        """
        if url not in self.extractors:
            raise KeyError(f"Unknown URL {url}")
        
        return self.extractors[url](url)
        


DEFAULT_EXTRACTOR: Extractor = Extractor()

def extract(url: Url, extractor=DEFAULT_EXTRACTOR) -> Bible:
    return DEFAULT_EXTRACTOR.extract(url)

def extractor(*args, **kwargs):
    return DEFAULT_EXTRACTOR.extractor(*args, **kwargs)


# Default extractor only supports 2 pages


#_CHAPTER_NAME_REGEX = re.compile(r"^\s*CHAPTER\s+\d+\s*$")
#_DIGIT_REGEX = re.compile(r"\d+")
#
#@DEFAULT_EXTRACTOR.extractor("http://www.jesus-is-lord.com/thebible.htm")
#def jesus_is_lord_extractor(url: Url) -> Bible:
#    main_page = BeautifulSoup(http.get(url).text, "html5lib")
#    # the second table contains all the links
#    table = main_page.find_all("table")[1]
#    old_test = table.find(string="Old Testament").parent.parent.find_all("a")
#    new_test = table.find(string="New Testament").parent.parent.find_all("a")
#    
#    # a list of old testimate and new testimate names
#    old_test_names = { test.text.lower() for test in old_test }
#    new_test_names = { test.text.lower() for test in new_test }
#    
#    # mapping of names to urls
#    bible_urls = OrderedDict([ (book.text.lower(), book.attrs["href"])
#            for book in old_test + new_test ])
#    
#    bible = Bible()
#    books: Dict[str, BibleBook] = OrderedDict()
#    for book_name, book_url in bible_urls.items():
#        book_url = urljoin(url, book_url) # full url
#        log.info(f"Processing book '{book_name}' from '{book_url}'")
#        
#        log.info("Downloading ...")
#        book_html = BeautifulSoup(http.get(book_url).text, "html5lib")
#        log.info("done")
#        
#        # Chapters are in special paragraphs. Use them to split the flow
#        verse_texts = book_html.select(".MsoNormal")
#        # delete book_html because it's probably taking up a lot of memory
#        del book_html
#        
#        
#        # split the verse_texts into chapters
#        chapter_indices = [ i for i, html in enumerate(verse_texts)
#                if _CHAPTER_NAME_REGEX.match(html.text) ]
#        # skip ch1
#        chapter_verses = []
#        prev_idx = -1
#        for ch_idx in chapter_indices + [len(verse_texts)]:
#            if prev_idx == -1:
#                prev_idx = ch_idx
#                continue # skip first one
#            chapter_verses.append(verse_texts[prev_idx+1:ch_idx])
#            prev_idx = ch_idx 
#        # chapters is a list of lists of verses
#        # Each list consists of the verses for chapter index + 1
#            
#            
#        chapters: Dict[int, List[BibleVerse]] = {}
#        #?import pdb; pdb.set_trace()
#        for chapter_idx, chap_verses in enumerate(chapter_verses):
#            # each text has a number before the actual text except the first one
#            verses = [ BibleVerse(num=1, text=chap_verses[0].text) ]
#            split_verses = ( verse.text.split(" ") for verse in chap_verses[1:] )
#            # Some numbers have weird chars appended to them.
#            # just extract the first number using _DIGIT_REGEX
#            verses += [ BibleVerse(num=int(_DIGIT_REGEX.match(split[0]).group(0)), 
#                text=" ".join(split[1:]))
#                    for split in split_verses if _DIGIT_REGEX.match(split[0])]
#            
#            chapters[chapter_idx+1] = verses
#            
#        books[book_name] = BibleBook(book_name, chapters)
#    
#    bible = Bible(books, old_test_names, new_test_names)
#    errors = bible.check()
#    for err in errors:
#        log.error(err)
#    if len(err) == 0:
#        log.info("No errors in bible")
#    return bible
#
#@DEFAULT_EXTRACTOR.extractor("http://ebible.org/eng-lxx2012/")
#def ebible_extractor(url: Url) -> Bible:
#    # this website only gives old testimate
#    # get info through Json
#    info = http.get("http://ebible.org/study/content/texts/ENGLXX/info.json").json()
#    sections = OrderedDict([ (
#        division,
#        [ sec for sec in info["sections"] if sec.startswith(info["divisions"][i]) ]
#        ) for i, division in enumerate(info["divisionNames"])
#        ])
#
#    SECTION_URL = "http://ebible.org/study/content/texts/ENGLXX/{}.html"
#    
#    VERSE_CLS_REGEX = re.compile("v-(\d+)(-\d+)?")
#    # download and parse the sections
#    # make the bible
#    books: Dict[str, BibleBook] = {}
#    warning: List[BibleWarning] = []
#    for book, secs in sections.items():
#        sec: Dict[int, BibleVerse] = {}
#        for sec_code in secs:
#            # download the section
#            sec_page = BeautifulSoup(http.get(SECTION_URL.format(sec_code)).text, "html5lib")
#            for verse_text in sec_page.find_all(class_="v-num"):
#                verse_matches = (VERSE_CLS_REGEX.fullmatch(cls) for cls in verse_text.attrs["class"])
#                try:
#                    verse_match = next(vm for vm in verse_matches if vm) # first match
#                except StopIteration:
#                    import pdb; pdb.set_trace()
#                verse_num = int(verse_match.group(1))
#                
#                # the text without the span that has the verse number
#                parent = verse_text.parent
#                verse = parent.text[len(parent.find_next().text):].strip()
#                
#                if verse_match.group(2):
#                    # register the warning
#                    w = BibleWarning(
#                            loc=BibleLocation(book=book, chapter=verse_num, verse=verse),
#                            type=BibleWarningType.MISSING,
#                            description=f"Found bible range {verse}-{verse_match.group(2)}. I'm assuming they're missing and assigning the text to {verse}")
#                    warning.append(w)
#                    
#                sec[verse_num] = BibleVerse(num=verse_num, text=verse)
#                    
#        books[book.lower()] = BibleBook(book_name=book, chapters=sec)
#
#    return Bible(books, books.keys(), [], warnings=warnings)
#
#@DEFAULT_EXTRACTOR.extractor("http://biblehub.com/kj2000/matthew/6.htm")
#def biblehub_extractor(url: Url) -> Bible:
#    ...
