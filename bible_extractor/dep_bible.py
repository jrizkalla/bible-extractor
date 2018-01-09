"""
Provides the main Bible-containing data structure.
"""

import enum
from typing import NamedTuple, Dict, Set, List, Iterable, Any, Union

class BibleLocation(NamedTuple):
    book: str
    chapter: int
    verse: int

BibleLocation.__str__ = lambda s: f"{s.book} {s.chapter}:{s.verse}"
def _loc_from_str(cls, s):
    book, rest = s.split(" ")
    chapter, verse = rest.split(":")
    return cls(book=book, chapter=int(chapter), verse=int(verse))
BibleLocation.from_str = classmethod(_loc_from_str)

class BibleVerse(NamedTuple):
    num: int
    text: str

class BibleBook:
    def __init__(self, book_name: str, chapters: Dict[int, List[BibleVerse]]) -> None:
        self.name = str(book_name)
        self.chapters: Dict[int, List[BibleVerse]] = { i : list(verses) 
                for i, verses in chapters.items() }
        
    __repr__ = lambda s: f"<BibleBook {s.name} with {len(s.chapters)} chapters>"
    __str__  = lambda s: f"The book of {s.name}"
    
    def json(self) -> Dict[Any, Any]:
        """
        Convert the book to JSON.
        """
        return self.chapters
    
SQL_BOOK    = object()
SQL_CHAPTER = object()
SQL_VERSE   = object()
SQL_TEXT    = object()

class BibleWarningType(enum.Enum):
    MISSING = enum.auto()
    
class BibleWarning(NamedTuple):
    loc: BibleLocation
    type: BibleWarningType
    description: str

class Bible:
    
    @classmethod
    def from_json(cls, data: Union[Dict[Any, Any], str]) -> "Bible":
        if isinstance(data, str):
            data = json.loads(data)
        
        return Bible(
                books=data["old_testimate"] + data["new_testimate"],
                old_testimate=(t for t in data["old_testimate"].keys()),
                new_testimate=(t for t in data["new_testimate"].keys()),
                warnings=( BibleWarning(
                    loc=BibleWarning.from_str(w["loc"]),
                    type=BibleWarningType(w["type"]),
                    description=w["desc"]
                    ) for w in data["warnings"] )
                )
    
    def __init__(self, books: Dict[str, BibleBook],
            old_testimate: Iterable[str], new_testimate: Iterable[str],
            warnings: Iterable[BibleWarning]=[]) -> None:
        self.books = dict(books)
        self.old_testimate = set(old_testimate)
        self.new_testimate = set(new_testimate)
        self.warnings = list(warnings)
        
    __repr__ = lambda s: f"<Bible {len(books)}"
    __str__  = lambda s: f"The Holy Bible"
    
    def __contains__(self, loc: BibleLocation) -> bool:
        try:
            _ = self[loc]
        except KeyError:
            return False
        else:
            return True
        
        
    def __getitem__(self, loc: BibleLocation) -> BibleVerse:
        book, chapter, verse = loc
        return self.books[book].chapters[chapter].verses[verse]
    
    
    def __iter__(self):
        for book in self.books:
            for chapter in book.chapters:
                for verse in chapter.verses:
                    yield (
                            BibleLocation(book, chapter, verse),
                            verse
                            )
    
    def json(self) -> Dict[Any, Any]:
        """
        Convert the bible to JSON
        """
        return {
                "warnings": [ { 
                        "loc": str(w.loc),
                        "type": str(w.type),
                        "desc": str(w.description)
                        } for w in self.warnings ],
                "bible": {
                    "old_testimate": { b.name: b.json() 
                        for b in self.books.values() if b.name in self.old_testimate },
                    "new_testimate": { b.name: b.json() 
                        for b in self.books.values() if b.name in self.new_testimate },
                    },
                }
        
    def sql(self, table_name: str, **table: Dict[str, Any]) -> str:
        """
        Convert the bible into SQL insert statments.
        One sql insert statment is issued for each verse and it has schema defined by table.
        
        The keys of table are the column names.
        If the value is one of SQL_* defined above, the appropriate values is substituted,
        otherwise, repr(value) is inserted.
        
        Note: neither the table name nor the column names are sanitized.
        Basic sanitation is applied on values but it should not be trusted.
        """
        
        
        table_data: List[Tuple[str]] = []
        for book in self.books.values():
            print(f"Processing book {book.name}")
            
            for chapter_num, chapter in book.chapters.items():
                for verse_num, verse_text in chapter:
                    row = list(table.values())
                    for i in range(len(row)):
                        col = row[i]
                        if col is SQL_BOOK:
                            row[i] = book.name
                        elif col is SQL_CHAPTER:
                            row[i] = chapter_num
                        elif col is SQL_VERSE:
                            row[i] = verse_num
                        elif col is SQL_TEXT:
                            row[i] = verse_text
                        row[i] = repr(row[i])
                    # sanitize the row
                    table_data.append(row)
                
        col_names = ", ".join(table.keys())
        return "\n".join(f"INSERT INTO {table_name} ({col_names})\nVALUES"
                f"  ({', '.join(row)});" for row in table_data)
        
        
    def check(self) -> List[str]:
        """
        Check for errors.
        :return: a (possibly) empty list of errors.A
        
        Checks:
            1. Chapters are not missing
            
        """
        
        errors: List[str] = []
        
        for book in self.books.values():
            for chap_num, chapter in book.chapters.items():
                max_verse = max(v.num for v in chapter)
                for verse_num in range(max_verse+1):
                    if chapter[verse_num-1].num != verse_num:
                        errors.append(f"Inconsistent verse number in chapter {chap_num} in book {book.name}")
        return errors
