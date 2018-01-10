from collections import defaultdict
import typing as T

from .bible import Bible, Verse, Testament

class BibleStats:
    _ATTRIBUTES = set("num_books,num_verses_per_chapter,num_warnings"
            .split(","))
    def __init__(self):
        self.num_books = [0, 0]
        self.num_verses_per_chapter: T.Dict[str, T.Dict[str, T.Dict[int, int]]] = {}
        self.num_warnings = 0
    
    def to_dict(self) -> T.Dict[str, T.Any]:
        res: T.Dict[str, T.Any] = {}
        for key in type(self)._ATTRIBUTES:
            res[key] = self.__dict__[key]
        return res

def get_bible_stats(bible: Bible) -> BibleStats:
    stats = BibleStats()
    
    for test in (Testament.old, Testament.new):
        test_name = "old" if test == Testament.old else "new"
        stats.num_verses_per_chapter[test_name] = {}
        
        for book in bible.testaments[test.value]:
            stats.num_verses_per_chapter[test_name][book] = {}
            stats.num_books[test.value] += 1
            
            for chap_num, chap in bible.verses[book].items():
                print(f"Looking at {chap_num}")
                stats.num_verses_per_chapter[test_name][book][chap_num] = 0
                
                for _ in chap.items():
                    stats.num_verses_per_chapter[test_name][book][chap_num] += 1
    return stats
