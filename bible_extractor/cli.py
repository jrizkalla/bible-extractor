from argparse import ArgumentParser
from os import path
import sys
import json
import pickle

import logging
logging.basicConfig(level=logging.INFO)

from .extract import DEFAULT_EXTRACTOR, extract
from .bible import SQL_BOOK, SQL_TEXT, SQL_VERSE, SQL_CHAPTER

ARG_PARSER = ArgumentParser(description="Extract The Bible from specific sources online")
ARG_PARSER.add_argument("source", help="The source to extract from. Use list for a list of sources")
ARG_PARSER.add_argument("-o", "--output", help="The output file",
        metavar="FILE", default="output.json")
ARG_PARSER.add_argument("-f", "--format", 
        help="The format, one of json or sql. "
        "The default is sql or the extensions of the output file",
        metavar="FORMAT", default="NONE", choices=("SQL", "JSON"))
ARG_PARSER.add_argument("-v", "--verbose", help="Increase verbosity level",
        action="count")


def main(args=None):
    if args is None:
        args = ARG_PARSER.parse_args()
        
    args.source = args.source.lower()
    if args.source == "list":
        print("Sources")
        
        for i, source in enumerate(DEFAULT_EXTRACTOR.extractors.keys()):
            print(f"{i:>4}    {source}")
        sys.exit(1)
    elif (args.source.isnumeric() 
            and int(args.source) >= 0 
            and int(args.source) < len(DEFAULT_EXTRACTOR.extractors)):
        source = list(DEFAULT_EXTRACTOR.extractors.keys())[int(args.source)]
    elif args.source in DEFAULT_EXTRACTOR.extractors.values():
        source = args.source
    else:
        print("Unknown source. Use list to list sources.", file=sys.stderr)
        sys.exit(1)
        
    if path.exists(args.output):
        answer = input(f"The file '{args.output}' exists. "
                "Do you want to override it? (y/n) ")
        answer = answer.lower()
        if answer not in ("yes", "y", "yeah"):
            sys.exit(1)
            
    if args.format != "NONE":
        fmt = args.format
    else:
        _, file_ext = path.splitext(args.output)
        if file_ext == ".json":
            fmt = "JSON"
        else:
            fmt = "SQL"
        
    result = extract(source)
    with open("test.pkl", "wb") as test_file:
        pickle.dump(result, test_file)
    #?with open("test.pkl", "rb") as test_file:
        #?result = pickle.load(test_file)
    #?print(result.check())
    if fmt == "JSON":
        with open(args.output, "w") as json_file:
            json.dump(result.json(), json_file)
    else:
        with open(args.output, "w") as sql_file:
            sql_text = result.sql("t_kjv", 
                b=SQL_BOOK,
                c=SQL_CHAPTER,
                v=SQL_VERSE,
                t=SQL_TEXT)
            sql_file.write(sql_text)
