import json
import sys

with open(sys.argv[1], "r") as json_file:
    bible = json.load(json_file)

for _, test in bible["testaments"].items():
    for chap_name, chaps in test.items():
        for chap_num, chap in chaps.items():
            for verse_num, verse in chap.items():
                if len(verse) < 10:
                    print(f"WARNING: {chap_name} {chap_num}:{verse_num} is small")
