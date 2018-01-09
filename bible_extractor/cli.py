from argparse import ArgumentParser
from os import path
import sys
import json
import pickle

import logging
logging.basicConfig(level=logging.INFO)

import typing as T

from .extract import DEFAULT_EXTRACTOR, extract
from . import extractors
from .bible import Bible
#?from .bible import SQL_BOOK, SQL_TEXT, SQL_VERSE, SQL_CHAPTER

ARG_PARSER = ArgumentParser(description="Extract The Bible from specific sources online")
ARG_PARSER.add_argument("source", nargs="+",
        help="The source to extract from. Use list for a list of sources. If multiple sources are specified, merge them (giving priority to the first source")
ARG_PARSER.add_argument("-o", "--output", help="The output file",
        metavar="FILE", default="output.json")
ARG_PARSER.add_argument("-f", "--format", 
        help="The format, one of json or sql. "
        "The default is sql or the extensions of the output file. If ALL is specificed, one of each format is created with the following filename scheme {output_file_name}.{format}",
        metavar="FORMAT", default="NONE", choices=("SQL", "JSON", "ALL"))
ARG_PARSER.add_argument("-v", "--verbose", help="Increase verbosity level",
        action="count")


def main(args=None):
    log = logging.getLogger(__name__ + ".main")
    if args is None:
        args = ARG_PARSER.parse_args()
        
    args.sources = [ s.lower() for s in args.source ]
    if "list" in args.sources:
        print("Sources")
        
        for i, source in enumerate(DEFAULT_EXTRACTOR.extractors.keys()):
            print(f"{i:>4}    {source}")
        if len(DEFAULT_EXTRACTOR.extractors) == 0:
            print("    NONE")
        sys.exit(1)
    # convert the sources:
    sources = []
    src_is_url = []
    for source in args.sources:
        is_url = True
        if (source.isnumeric() 
                and int(source) >= 0 
                and int(source) <= len(DEFAULT_EXTRACTOR.extractors)):
            source = list(DEFAULT_EXTRACTOR.extractors.keys())[int(source)]
        elif source in DEFAULT_EXTRACTOR.extractors.values():
            # do nothing
            ...
        else:
            # source is a file
            log.info(f"Treating {source} as a file not a URL")
            is_url = False
        sources.append(source)
        src_is_url.append(is_url)
        
    if path.exists(args.output):
        answer = input(f"The file '{args.output}' exists. "
                "Do you want to override it? (y/n) ")
        answer = answer.lower()
        if answer not in ("yes", "y", "yeah"):
            sys.exit(1)
            
    fmts: T.List[str] = []
    all_selected = False
    if args.format == "ALL":
        fmts += ["JSON", "SQL"]
        all_selected = True
    elif args.format != "NONE":
        fmts.append(args.format)
    else:
        _, file_ext = path.splitext(args.output)
        if file_ext == ".json":
            fmts.append("JSON")
        else:
            fmts.append("SQL")
        
    result = Bible()
    for is_url, source in zip(src_is_url, sources):
        if is_url:
            bible = extract(source)
        else:
            with open(source, "r") as json_file:
                bible = Bible.from_dict(json.load(json_file))
        result.merge(bible)
    #?with open("test.pkl", "rb") as test_file:
        #?result = pickle.load(test_file)
    #?print(result.check())
    for fmt in fmts:
        if all_selected:
            out_file = f"{args.output}.{fmt.lower()}"
        else:
            out_file = args.output
        if fmt == "JSON":
            with open(out_file, "w") as json_file:
                json.dump(result.to_dict(), json_file, indent=2)
        else:
            with open(out_file, "w") as sql_file:
                sql_text = "NOT IMPLEMENTED"
#?                sql_text = result.sql("t_kjv", 
#?                    b=SQL_BOOK,
#?                    c=SQL_CHAPTER,
#?                    v=SQL_VERSE,
#?                    t=SQL_TEXT)
                sql_file.write(sql_text)
