"""
Provides the main Bible-containing data structure.
"""

from typing import NamedTuple, Dict, Set, List, Iterable

class BibleVerse(NamedTuple):
    num: int
    text: str

class BibleBook:
    def __init__(self, book_name: str, chapters: Dict[int, List[BibleVerse]]) -> None:
        self.book_name = str(book_name)
        self.chapters: Dict[int, List[BibleVerse]] = { i : list(verses) 
                for i, verses in chapters.items() }
        
    __repr__ = lambda s: f"<BibleBook {book_name} with {len(chapters)} chapters>"
    __str__  = lambda s: f"The book of {book_name}"
    

class Bible:
    def __init__(self, books: Dict[str, BibleBook],
            old_testimate: Iterable[str], new_testimate: Iterable[str]) -> None:
        self.books = dict(books)
        self.old_testimate = set(old_testimate)
        self.new_testimate = set(new_testimate)
        
    __repr__ = lambda s: f"<Bible {len(books)}"
    __str__  = lambda s: f"The Holy Bible"
