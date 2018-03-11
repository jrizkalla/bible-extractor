#!/usr/bin/env python3

import sys
import argparse
import json

version = sys.version_info
if version.major < 3 or version.minor < 6:
    print("{} needs python 3.6 or higher to run".format(sys.argv[0]),
            file=sys.stderr)
    sys.exit(1)
del version

parser = argparse.ArgumentParser(description="Compare two bible stat Json files.")
parser.add_argument("stat1_fn")
parser.add_argument("stat2_fn")
parser.add_argument("--name1", default="stat1")
parser.add_argument("--name2", default="stat2")

def main(stat1_fn, stat2_fn, name1, name2):
    with open(stat1_fn, "r") as stat1_f:
        stat1 = json.load(stat1_f)[0]["num_verses_per_chapter"]
    with open(stat2_fn, "r") as stat2_f:
        stat2 = json.load(stat2_f)[0]["num_verses_per_chapter"]
    
    # compare them
    books1_old = set(stat1["old"])
    books1_new = set(stat1["new"])
    books2_old = set(stat2["old"])
    books2_new = set(stat2["new"])
    books1 = books1_old.union(books1_new)
    books2 = books2_old.union(books2_new)
    
    print("Books:")
    b1_b2 = books1 - books2
    b2_b1 = books2 - books1
    print(f"{name1} has {len(b1_b2)} books not in {name2}:")
    for b in b1_b2:
        test = "OT" if b in books1_old else "NT"
        print(f"\t- ({test})  {b}")
    print(f"{name2} has {len(b2_b1)} books not in {name1}:")
    for b in b2_b1:
        test = "OT" if b in books2_old else "NT"
        print(f"\t- ({test}) {b}")
    print()
        
    books = books1.intersection(books2)
    # combine old and new
    stat1 = { **stat1["old"], **stat1["new"] }
    stat2 = { **stat2["old"], **stat2["new"] }
    # For each book, print the chapters that don't match
    print(f"\nLooking at {len(books)} books in both Bibles\n")
    for book in books:
        chapters = set(int(c) for c in stat1[book].keys()).union(
                set(int(c) for c in stat2[book].keys()))
        chapters = sorted(chapters)
        for chap in chapters:
            chap_name = str(chap)
            try:
                if stat1[book][chap_name] != stat2[book][chap_name]:
                    print(f"{book:>20} {chap:3}: {name1} has "
                            f"{stat1[book][chap_name]:3} verse(s) but {name2} "
                            f"has {stat2[book][chap_name]:3} verse(s)")
            except KeyError:
                # chapter not in one of them
                name = name2 if chap_name in stat1[book] else name1
                print(f"{book}: chapter {chap} is missing from {name}")
        
    
if __name__ == "__main__":
    main(**vars(parser.parse_args()))
