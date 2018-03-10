import copy

from ..bible import *


def _remove(bible: Bible, test: Testament) -> Bible:
    b = Bible(bible.name)
    for verse in (v for v in bible if v.loc.test != test):
        b += verse
    
    b.warnings = copy.deepcopy(bible.warnings)
    return b

def remove_old(bible: Bible) -> Bible:
    """Remove the old testament."""
    return _remove(bible, Testament.old)
    

def remove_new(bible: Bible) -> Bible:
    """Remove the old testament."""
    return _remove(bible, Testament.new)
