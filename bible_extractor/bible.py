import enum
import typing as T
from collections import OrderedDict
import logging
log = logging.getLogger(__name__)

class Testament(enum.Enum):
    old = 0
    new = 1
    unknown = -1

class Verse:
    class Loc(T.NamedTuple):
        book: str
        chapter: int
        verse: int
        test: Testament
    # monkey patch Loc to add a default argument
    Loc.__new__.__defaults__ = (Testament.unknown, )
    Loc.__repr__ = lambda l: f"Verse.Loc(book={repr(l.book)}, chapter={repr(l.chapter)}, verse={repr(l.verse)}, test={str(l.test)})"
    Loc.__str__ = lambda l: "{}{}".format(l.book, " {}{}".format(l.chapter, 
        ":{}".format(l.verse) if l.verse > 0 else "")
            if l.chapter > 0 else "")
    
    
    def __init__(self, loc: Loc, text: str = ""):
        assert isinstance(loc, Verse.Loc)
        self.loc = loc
        self.content = text
    
    def __repr__(self):
        return f"Verse({repr(self.loc)})"
    def __str__(self):
        return self.content
    
class BibleInconsistentError(Exception):
    ...
    
class Bible:
    
    @classmethod
    def from_dict(cls, data) -> "Bible":
        bible = Bible(name = data.get("name", ""))
        for test_name, test in zip(("old", "new"), (Testament.old, Testament.new)):
            # use order for iteraton to preserve order
            for book_name in data["order"][test_name]:
                book = data["testaments"][test_name][book_name]
                for chap_num, chap in book.items():
                    for verse_num, verse in chap.items():
                        bible += Verse(Verse.Loc(book_name, 
                            int(chap_num),
                            int(verse_num), test), str(verse))
        return bible
        
    
    def __init__(self, name="") -> None:
        self.name = str(name)
        self.verses: T.Dict[str, T.Dict[int, T.Dict[int, str]]] = OrderedDict({})
        self.testaments: T.List[T.List[str]] = [[], []]

    def __getitem__(self, loc: Verse.Loc) -> Verse:
        is_old_t = loc.book in self.testaments[Testament.old.value]
        v_loc = Verse.Loc(loc.book,
                loc.chapter,
                loc.verse,
                Testament.old if is_old_t else Testament.new)
        return Verse(v_loc, self.verses[loc.book][loc.chapter][loc.verse])
    
    def __contains__(self, loc: Verse.Loc) -> bool:
        try:
            _ = self.verses[loc.book][loc.chapter][loc.verse]
        except KeyError:
            return False
        else:
            return True
    
    def __setitem__(self, loc: Verse.Loc, text: str):
        # make sure the book can be placed in old or new testament
        if loc.test != Testament.unknown:
            if loc.book in self.testaments[(loc.test.value + 1) % 2]:
                # it's in the other testament. Raise an error
                raise BibleInconsistentException("a book cannot be in both testaments")
            if loc.book not in self.testaments[loc.test.value]:
                self.testaments[loc.test.value].append(loc.book)
        else:
            book = loc.book
            if all(book not in self.testaments[t.value] 
                    for t in (Testament.old, Testament.new)):
                raise BibleInconsistentError("a book has to be in one of the testaments")
        
        book = self.verses.get(loc.book, OrderedDict({}))
        chapter = book.get(loc.chapter, OrderedDict({}))
        chapter[loc.verse] = text
        
        book[loc.chapter] = chapter
        self.verses[loc.book] = book
    
    def __iadd__(self, verse: Verse):
        self[verse.loc] = verse.content
        return self
    
    def __iter__(self) -> T.Generator[Verse, None, None]:
        for t in (Testament.old, Testament.new):
            yield from self.iter(t)
    
    def iter(self, t: Testament) -> T.Generator[Verse, None, None]:
        for book in self.testaments[t.value]:
            for chap_n, chap in self.verses[book].items():
                for verse_n, verse in chap.items():
                    yield Verse(Verse.Loc(book, chap_n, verse_n, t), verse)
                    
    def warn(self, locs: T.Union[Verse.Loc, T.Iterable[Verse.Loc]], text: str):
        try:
            locs = list(locs)
        except TypeError:
            locs = [ locs ]
        log.warn(f"{str(locs[0])}: {text}")
        
    
    
    def to_dict(self) -> T.Dict[str, T.Any]:
        return {
                "name": self.name,
                "testaments": {
                    "old": { b: dict(self.verses[b]) 
                        for b in self.testaments[Testament.old.value] },
                    "new": { b: dict(self.verses[b]) 
                        for b in self.testaments[Testament.new.value] }
                    },
                "order": {
                    "old": list(self.testaments[Testament.old.value]),
                    "new": list(self.testaments[Testament.new.value]),
                    }
                }
        
        
    def merge(self, other: "Bible"):
        if self.name.strip() == "":
            self.name = other.name
        self.verses = other.verses
        self.testaments = other.testaments
    
    
    def __repr__(self) -> str:
        num_old = len(self.testaments[Testament.old.value])
        num_new = len(self.testaments[Testament.new.value])
        return f"<Bible {num_old} old and {num_new} new testaments>"
    
    def __str__(self) -> str:
        return f"{self.name} bible"
