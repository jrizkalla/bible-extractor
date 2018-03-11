import logging
import re
from collections import OrderedDict
import typing as T

import requests as http
from bs4 import BeautifulSoup

from ..extract import extractor, Url
from ..bible import Bible, Verse, Testament
from ..util import fix_book_name
from .. import warnings as warn

# a blacklist of strings to replace
STR_BLACKLIST: T.Dict[str, str] = {}
# helper used for substituting regex matches (for STR_BLACKLIST)
def _string_fixer(m): return STR_BLACKLIST.get(m.group(0), m.group(0))


_VERSE_CLS_REGEX = re.compile("v-(\d+)(-\d+)?")

def _is_text_tag(tag):
    """
    Returns `True` if a tag is part of a Bible verse and `False` if it's just formatting.
    """
    if tag.name is None:
        return True
    classes = set(tag.attrs.get("class", []))
    if any(_VERSE_CLS_REGEX.match(cls) for cls in classes):
        return False
    elif len(set(["notemark", "note"]).intersection(classes)) > 0:
        return False
    else: return True
    
def _to_str(tag_or_str):
    try:
        return tag_or_str.text
    except AttributeError:
        return str(tag_or_str)
    

@extractor("http://ebible.org/eng-lxx2012/")
def ebible_extractor(url: Url) -> Bible:
    
    # compile regex for fixing the text (STR_BLACKLIST)
    blacklist_regex = re.compile("|".join(f"({re.escape(k)})" 
        for k in STR_BLACKLIST.keys()))
    
    log = logging.getLogger(__name__)
    bible = Bible(name="Septuagint in American English")
    
    info = http.get("http://ebible.org/study/content/texts/ENGLXX/info.json").json()
    sections = OrderedDict([ (
        (division, info["divisions"][i]),
        [ sec for sec in info["sections"] if sec.startswith(info["divisions"][i]) ]
        ) for i, division in enumerate(info["divisionNames"])
        ])
    
    num_chapters = sum(len(chap) for chap in sections.values())

    SECTION_URL = "http://ebible.org/study/content/texts/ENGLXX/{}.html"
    
    # download and parse the sections
    # make the bible
    EXTRACT_NUM_REGEX = re.compile(r"^[^\d]*(\d+)$")
    chap_count = -1
    for (book, div), chapters in sections.items():
        for chap_code in chapters:
            chap_count += 1
            log.info(f"({chap_count*100 // num_chapters:3}%) Extracting chapter "
                    f"{chap_code} in {book} (corrected: {fix_book_name(book)})")
            # get the chapter number
            try:
                # the chapter name sometimes ends with a numbers (e.g. Kings 1)
                # so remove the name from the string before attempting to parse it
                actual_chap_code = chap_code[len(div):]
                chap_num = int(EXTRACT_NUM_REGEX.match(actual_chap_code).group(1))
            except (AttributeError, ValueError):
                book.warn(Verse.Loc(book, -1, -1), 
                        f"Unknown chapter number. Chapter code is {chap_code}",
                        warn.unknown_chap_num)
                continue
            
            chap_page = BeautifulSoup(
                    http.get(SECTION_URL.format(chap_code)).text, "html5lib")
            
            for verse_html in chap_page.find_all(class_="v-num"):
                verse_matches = (_VERSE_CLS_REGEX.fullmatch(cls) 
                        for cls in verse_html.attrs["class"])
                try:
                    verse_match = next(vm for vm in verse_matches if vm) # first match
                except StopIteration:
                    bible.warn(Verse.Loc(fix_book_name(book), chap_num, -1), "Cannot find verses",
                            warn.cannot_find_verse)
                    continue
                try:
                    verse_num = int(verse_match.group(1))
                except (AttributeError, ValueError):
                    bible.warn(Verse.Loc(fix_book_name(book), chap_num, -1), "Cannot find verse number",
                            warn.cannot_find_verse_num)
                    continue
                
                parent = verse_html.parent
                verse = "".join( _to_str(c) for c in parent if _is_text_tag(c) ).strip()
                # remove multiple spaces
                verse = " ".join(verse.split())
                # filter stuff from STR_BLACKLIST from verse
                verse = blacklist_regex.sub(_string_fixer, verse)
                if verse_match.group(2):
                    # More than one verse
                    locs = [
                            Verse.Loc(fix_book_name(book), chap_num, v)
                            for v in range(verse_num, int(verse_match.group(2)[1:])+1)
                            ]
                    bible.warn(locs, "Found bible range. Merging into the first verse.",
                            warn.verse_range)
                
                bible += Verse(Verse.Loc(fix_book_name(book), chap_num, verse_num, Testament.old), verse)
    return bible


STR_BLACKLIST = {
        "\u00e2\u0080\u0094": " ",
        "\u00e2\u008c\u0083": "",
        "\u00e2\u0080\u0099": "'"
        }
