import sys

from ..bible import *

def check_lengths(bible: Bible):
    """
    Print a warning (to stderr) for 
every verse that's less than 10 characters long.
    """
    
    for verse in bible:
        if len(verse.content) < 10:
            book, chap, verse_num, _ = verse.loc
            print(f"WARNING:check_lengths:{book} {chap}:{verse_num} is small",
                file=sys.stderr)
    return bible
