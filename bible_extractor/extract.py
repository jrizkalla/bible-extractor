"""
Provides functions to extract the data from websites.
"""
from typing import NewType, Callable, no_type_check
from collections import OrderedDict
from urllib.parse import urljoin
import re

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
        self.extractors: Dict[Url, ExtractorFunc] = {}
    
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


# Default extractor only supports 2 pages


_CHAPTER_NAME_REGEX = re.compile(r"^\s*CHAPTER\s+\d+\s*$")
_DIGIT_REGEX = re.compile(r"\d+")

@DEFAULT_EXTRACTOR.extractor("http://www.jesus-is-lord.com/thebible.htm")
def jesus_is_lord_extractor(url: Url) -> Bible:
    main_page = BeautifulSoup(http.get(url).text, "html5lib")
    # the second table contains all the links
    table = main_page.find_all("table")[1]
    old_test = table.find(string="Old Testament").parent.parent.find_all("a")
    new_test = table.find(string="New Testament").parent.parent.find_all("a")
    
    # a list of old testimate and new testimate names
    old_test_names = { test.text.lower() for test in old_test }
    new_test_names = { test.text.lower() for test in new_test }
    
    # mapping of names to urls
    bible_urls = OrderedDict([ (book.text.lower(), book.attrs["href"])
            for book in old_test + new_test ])
    
    books: Dict[str, BibleBook] = OrderedDict()
    for book_name, book_url in bible_urls.items():
        book_url = urljoin(url, book_url) # full url
        print(f"Processing book {book_name} from {book_url}")
        
        print(f"\tDownloading...\t", end="", flush=True)
        book_html = BeautifulSoup(http.get(book_url).text, "html5lib")
        print("Done", flush=True)
        
        # Chapters are in special paragraphs. Use them to split the flow
        verse_texts = book_html.select(".MsoNormal")
        # delete book_html because it's probably taking up a lot of memory
        del book_html
        
        
        # split the verse_texts into chapters
        chapter_indices = [ i for i, html in enumerate(verse_texts)
                if _CHAPTER_NAME_REGEX.match(html.text) ]
        # skip ch1
        chapter_verses = []
        prev_idx = -1
        for ch_idx in chapter_indices + [len(verse_texts)]:
            if prev_idx == -1:
                prev_idx = ch_idx
                continue # skip first one
            chapter_verses.append(verse_texts[prev_idx+1:ch_idx])
            prev_idx = ch_idx 
        # chapters is a list of lists of verses
        # Each list consists of the verses for chapter index + 1
            
            
        chapters: Dict[int, List[BibleVerse]] = {}
        #?import pdb; pdb.set_trace()
        for chapter_idx, chap_verses in enumerate(chapter_verses):
            # each text has a number before the actual text except the first one
            verses = [ BibleVerse(num=1, text=chap_verses[0].text) ]
            # TODO change to iterator
            split_verses = [ verse.text.split(" ") for verse in chap_verses[1:] ]
            try:
                # Some numbers have weird chars appended to them.
                # just extract the first number using _DIGIT_REGEX
                verses += [ BibleVerse(num=int(_DIGIT_REGEX.match(split[0]).group(0)), 
                    text=" ".join(split[1:]))
                        for split in split_verses if _DIGIT_REGEX.match(split[0])]
            except AttributeError:
                import pdb; pdb.set_trace()
            
            chapters[chapter_idx+1] = verses
            
        books[book_name] = BibleBook(book_name, chapters)
    
    return Bible(books, old_test_names, new_test_names)

