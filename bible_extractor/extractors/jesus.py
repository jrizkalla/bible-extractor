import logging
import re
from urllib.parse import urljoin
from collections import OrderedDict

import requests as http
from bs4 import BeautifulSoup

from ..extract import extractor, Url
from ..bible import Bible, Verse, Testament
from ..progress import ProgressIndicator


_CHAPTER_NAME_REGEX = re.compile(r"^\s*CHAPTER\s+\d+\s*$")
_DIGIT_REGEX = re.compile(r"\d+")

@extractor("http://www.jesus-is-lord.com/thebible.htm")
def jesus_is_lord_extractor(url: Url) -> Bible:
    log = ProgressIndicator(logging.getLogger(__name__))
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
    
    log.num_chapters = len(old_test_names) + len(new_test_names) # books instead of chapters
    i = -1
    
    bible = Bible()
    for book_name, book_url in bible_urls.items():
        i += 1
        log.starting(i, f"Extracting book {book_name} ('{book_url}')")
        book_url = urljoin(url, book_url) # full url
        
        book_html = BeautifulSoup(http.get(book_url).text, "html5lib")
        
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
            log.info(f"Processing chapter {chapter_idx+1} with {len(chap_verses)-1} verses")
            # each text has a number before the actual text except the first one
            split_verses = ( verse.text.split(" ") for verse in chap_verses[1:] )
            # Some numbers have weird chars appended to them.
            # just extract the first number using _DIGIT_REGEX
            for verse_idx, split in enumerate(split 
                    for split in split_verses if _DIGIT_REGEX.match(split[0])):
                test = (Testament.old 
                        if book_name in old_test_names else Testament.new)
                bible += Verse(Verse.Loc(book_name, chapter_idx+1, verse_idx+1, test),
                        " ".join(split[1:]))
                        
                
    return bible
