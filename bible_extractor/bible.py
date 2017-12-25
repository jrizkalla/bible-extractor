"""
Provides the main Bible-containing data structure.
"""

from typing import NamedTuple, Dict, Set, List, Iterable, Any

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

class Bible:
    def __init__(self, books: Dict[str, BibleBook],
            old_testimate: Iterable[str], new_testimate: Iterable[str]) -> None:
        self.books = dict(books)
        self.old_testimate = set(old_testimate)
        self.new_testimate = set(new_testimate)
        
    __repr__ = lambda s: f"<Bible {len(books)}"
    __str__  = lambda s: f"The Holy Bible"
    
    def json(self) -> Dict[Any, Any]:
        """
        Convert the bible to JSON
        """
        return {
                "old_testimate": { b.name: b.json() 
                    for b in self.books.values() if b.name in self.old_testimate },
                "new_testimate": { b.name: b.json() 
                    for b in self.books.values() if b.name in self.new_testimate },
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
