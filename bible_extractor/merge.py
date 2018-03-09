import copy
import typing as T
import logging

from .bible import *

_log = logging.getLogger(__name__)

def merge(*bibles: T.List[Bible]) -> Bible:
    try:
        result = copy.deepcopy(bibles[0])
    except IndexError:
        raise ValueError("Merge needs at least one bible") from None
    
    for bible in bibles[1:]:
        result = _merge_two(result, bible)
    
    return result

def _merge_two(b1: Bible, b2: Bible) -> Bible:
    b1.name = f"{b1.name} and {b2.name}"
    
    # go through b2 and see if there's anything not in b1
    locs_added: Set[Verse.Loc] = set()
    for verse in b2:
        if verse.loc not in b1:
            locs_add(verse.loc)
            b1 += verse
            _log.info(f"Taking {verse.loc} from '{b2.name}' into '{b1.name}'")
    
    # get all the warnings in b2 that have one of locs_added and put them in b1
    for warning in b2.warnings:
        if len(set(warning.locs).intersect(locs_added)) >= 0:
            warning_copy = copy.deepcopy(warning)
            warning_copy.text = f"{b2.name}: {warning.text}"
            b1.warnings.add(warning_copy)
            
    return b1
