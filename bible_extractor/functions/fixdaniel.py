import copy
from collections import OrderedDict
from copy import deepcopy

from ..bible import *

def fix_daniel(bible: Bible) -> Bible:
    """
    Fix Daniel in LXX according to https://docs.google.com/document/d/1wzM_RXZ0QXiZun7h371YhzJ4sYmYJlKlbtB43FjyFYI/edit.
    
    
    Steps:
    1. Merge verses 28 and 29 in "Prayer of Azarias" chapter 1
    2. Decrease all verses from 30 in "Prayer of Azarias" chapter 1
    3. Move "Susanna" to Chapter 13 of Daniel
    4. Move "Bel and the Dragon" to Chapter 14 of Daniel
    5. Move verses 23:... from Chapter 3 of Daniel to verses 91:100
    6. Move verses from chapter 1 of "Prayer of Azarias" to chapter 3 Daniel 25:90
    
    Note: verses 23 and 24 will be missing.
    """
    
    azarias = deepcopy(bible.verses["prayer of azarias"][1]) # chapter 1
    azarias[28] += " " + azarias[29]
    del azarias[29]
    shifted_azarias = OrderedDict()
    for k in range(30, max(azarias.keys())+1):
        shifted_azarias[k-1] = azarias[k]
        del azarias[k]
    azarias.update(shifted_azarias)
    
    # move on to step 3
    daniel = deepcopy(bible.verses["daniel"])
    daniel[13] = bible.verses["susanna"][1]
    daniel[14] = bible.verses["bel and the dragon"][1]
    sd = OrderedDict() # shifted daniel (chapter 3)
    for k in range(23, max(daniel[3].keys())+1):
        sd[k+68] = daniel[3][k]
        del daniel[3][k]
    daniel[3].update(sd)
    
    for k, v in azarias.items():
        daniel[3][24+k] = v
    
    # delete Azarias, susanna, and bel and the dragon
    newb = deepcopy(bible)
    for deleted in ("prayer of azarias", "susanna", "bel and the dragon"):
        del newb.verses[deleted]
        del newb.testaments[0][newb.testaments[0].index(deleted)]
    
    # reorder all the verses in daniel by verse number
    ordered_daniel = OrderedDict(
            (chap_num, 
                OrderedDict(sorted(chap.items(), key=lambda i: i[0])))
            for chap_num, chap in daniel.items())
    # udpate daniel
    newb.verses["daniel"] = ordered_daniel
    
    return newb
