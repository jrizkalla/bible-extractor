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
from ..util import fix_book_name

_VERSE_REGEX = re.compile("\s*\[\s*(\d+)\s*\]\s*")


@extractor("http://www.drbo.org/")
def drbo(url: Url) -> Bible:
    log = ProgressIndicator(logging.getLogger(__name__))
    bible = Bible(name="Douay-Rheims Bible")
    
    # get the names and links of the old and new testaments
    ot_links: T.Dict[str, str] = {}
    nt_links: T.Dict[str, str] = {}
    
    main_page = BeautifulSoup(http.get(url).text, "html5lib")
    ot_a_elems = main_page.select("td.OT1 a.b, td.OT2 a.b")
    nt_a_elems = main_page.select("td.NT a.b")
    ot_links = OrderedDict(
            ( next(s for s in elem.contents if isinstance(s, str)).strip()
            , elem["href"])
            for elem in ot_a_elems )
    nt_links = OrderedDict( 
            ( next(s for s in elem.contents if isinstance(s, str)).strip() 
            , elem["href"])
            for elem in nt_a_elems )
    links = ( ot_links, nt_links )
    
    log.num_chapters = len(ot_links) + len(nt_links)
    book_idx = -1
    for testament in (Testament.old, Testament.new):
        for name, chap_path in links[testament.value].items():
            book_idx += 1
            log.starting(book_idx, f"Extracting book {name}")
            
            chap_url = urljoin(url, chap_path)
            chapter_links = { 1 : chap_url }
            chap_page = BeautifulSoup(http.get(chap_url).text,
                    "html5lib")
            
            # we're in chapter 1, first get the rest of the chapters
            for a_tag in chap_page.select("table.chapnumtable a"):
                next_chap_url = a_tag["href"]
                try:
                    num = int(a_tag.string.strip(), base=10)
                except ValueError:
                    bible.warn(Verse.Loc(fix_book_name(name), -1, -1, testament), 
                            f"Unknown verse number {a.string.strip()}",
                            warn.unknown_verse_num)
                    continue
                
                if num in chapter_links:
                    bible.warn(Verse.Loc(fix_book_name(name), num, -1, testament),
                            f"Found chapter {num} twice",
                            warn.multiple_chapters)
                    continue
                chapter_links[num] = urljoin(urljoin(url, "chapter/"), next_chap_url)
                
            for chap_num, chap_path in chapter_links.items():
                log.info(f"Extracting chapter {chap_num}/{len(chapter_links)}")
                if chap_num != 1:
                    chap_page = BeautifulSoup(http.get(urljoin(url, chap_path)).text,
                            "html5lib")
                
                for para in chap_page.select("table.texttable td.textarea p"):
                    if (len({"desc", "note"}.intersection(set(para.attrs.get("class", []))))
                            != 0): continue
                    # get the first a tag
                    try:
                        a_tag = para.select("a")[0]
                    except IndexError:
                        bible.warn(Verse.Loc(fix_book_name(name), chap_num, -1, testament),
                                "Empty paragraph",
                                warn.empty_verse)
                        continue
                        
                    while a_tag is not None:
                        try:
                            verse_num = int(_VERSE_REGEX.match(a_tag.string).group(1),
                                    base=10)
                        except (AttributeError, ValueError):
                            import pdb; pdb.set_trace()
                            bible.warn(Verse.Loc(fix_book_name(name), chap_num, -1, testament),
                                    f"Unable to get verse number from '{a_tag.string}'")
                            a_tag = a_tag.next_sibling.next_sibling
                            continue
                        text = []
                        a_tag = a_tag.next_sibling
                        while a_tag is not None and a_tag.name != "a":
                            text.append(a_tag.string.strip())
                            a_tag = a_tag.next_sibling
                        text = " ".join(text)
                        bible += Verse(Verse.Loc(
                            fix_book_name(name), chap_num, verse_num, testament), text)
    return bible

