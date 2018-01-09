import typing as T

from .bible import *

def normalize(bible: Bible) -> Bible:
    def normstr(s): return s.lower().capitalize()
    def normloc(l): return BibleLocation(
            book=normstr(l.book),
            chapter=l.chapter,
            verse=l.verse
            )
        
    # normalize the book names
    return Bible(
            books=( (normstr(n), b) for n, b in bible.books.items() ),
            old_testimates=( normstr(t) for t in bible.old_testimates ),
            new_testimates=( normstr(t) for t in bible.new_testimates ),
            warnings = ( BibleWarning(
                loc=normloc(l),
                type=l.type,
                description=l.description) for l in bible.warnings )
            )

def merge(args: T.List[Bible]) -> Bible:
    """
    Merge bibles in descending order of prioirity
    """
    # merge them two by two
    res = args[0]
    for bible in args[1:]:
        res = merge_two(res, bible)
    return res

def merge_two(b1: Bible, b2: Bible) -> Bible:
    """
    Merge two bibles.
    """
    b1 = normalize(b1)
    b2 = normalize(b2)
    
    
    books: T.Dict[str, T.Dict[int, T.List[BibleVerse]]] = dict(b1.books)
    old = set(b1.old_testimates)
    new = set(b1.new_testimates)
    
    for loc, verse in b2:
        # if the verse is missing from b1, add it
        if loc not in b1:
            # does the book exist?
            if loc.book not in books:
                books[loc.book] = {}
                if loc.book in b2.old_testimates:
                    old.add(loc.book)
                else:
                    new.add(loc.book)
            # does the chapter exist
            if loc.chapter not in books[loc.book]:
                books[loc.book][loc.chapter] = []
            books[loc.book][loc.chapter].append(verse)
            
            
    return Bible(
            books=books,
            old_testimates=old,
            new_testimates=new,
            warnings=b1.warnings + b2.warnings)
