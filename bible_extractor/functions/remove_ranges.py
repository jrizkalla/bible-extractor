import copy
import logging

from ..bible import *
from .. import warnings as warn

def remove_ranges(bible: Bible) -> Bible:
    log = logging.getLogger(__name__)
    blacklist_locs = set()
    for warning in (w for w in bible.warnings if w.type == warn.verse_range):
        for loc in warning.locs:
            log.info(f"Skipping location {loc}")
            blacklist_locs.add(loc)
    
    # copy the bible...
    new_bible = Bible(bible.name)
    for verse in (v for v in bible if v.loc.remove_test() not in blacklist_locs):
        new_bible += verse
    
    new_bible.warnings = copy.deepcopy(new_bible.warnings)
    
    return new_bible
