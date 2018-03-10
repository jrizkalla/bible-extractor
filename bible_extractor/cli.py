from argparse import ArgumentParser
from os import path
import sys
import json
import pickle
import re

import logging
logging.basicConfig(level=logging.INFO)

import typing as T

from .extract import DEFAULT_EXTRACTOR, extract
from . import extractors
from .bible import Bible, Verse
from .stats import get_bible_stats
from .merge import merge
from . import functions

FUNCTIONS = functions.__all__

ARG_PARSER = ArgumentParser(description="Extract The Bible from specific sources online")
ARG_PARSER.add_argument("source", nargs="+",
        help=
"""The source to extract from. Use list for a list of sources. If multiple sources are specified, merge them (giving priority to the first source).
Each source has the following format: <filename or index>[:function ...]. 
Use list to get a list of functions.
""")
ARG_PARSER.add_argument("-o", "--output", help="The output file",
        metavar="FILE", default="output.json")
ARG_PARSER.add_argument("-f", "--format", 
        help="The format, one of json or sql. "
        "The default is sql or the extensions of the output file. If ALL is specificed, one of each format is created with the following filename scheme {output_file_name}.{format}",
        metavar="FORMAT", default="NONE", choices=("SQL", "JSON", "ALL"))
ARG_PARSER.add_argument("-s", "--stats", metavar="FILE", help="Output the statistics of the bible in FILE")
ARG_PARSER.add_argument("-v", "--verbose", help="Increase verbosity level",
        action="count")

def _print_list():
    print("Sources")
    
    for i, source in enumerate(DEFAULT_EXTRACTOR.extractors.keys()):
        print(f"{i:>4}    {source}")
    if len(DEFAULT_EXTRACTOR.extractors) == 0:
        print("    NONE")
    
    print("\nFunctions")
    for func in FUNCTIONS:
        desc = func.__doc__.strip().replace("\n", f"\n{' ' * (8 + 20 + 2)}")
        print(f"{func.__name__:20} {' ' * 8} {desc}")
        

_SOURCE_REGEX = re.compile(r"([^:]+)((:[^:]*)*)")
BibleFunc = T.Callable[[Bible], Bible]
class SourceParseError(Exception): pass
def parse_source(source: str) -> T.Optional[
        T.Tuple[bool, str, T.List[BibleFunc]]]:
    match = _SOURCE_REGEX.match(source)
    if match is None: raise SourceParseError()
    
    src = match.group(1)
    func_names = match.group(2)
    funcs: T.List[BibleFunc] = []
    for func_name in func_names.split(":"):
        func_name = func_name.strip().lower().replace(" ", "_")
        if func_name == "":
            continue
        else:
            # find the function
            try:
                func = next(func for func in FUNCTIONS
                        if func.__name__ == func_name)
            except StopIteration:
                raise KeyError(func_name) from None
        funcs.append(func)
    
    try:
        int(src)
        is_idx = True
    except ValueError:
        is_idx = False
    
    return (is_idx, src, funcs)

def _apply_funcs(log, funcs: T.Iterable[BibleFunc], bible: Bible) -> Bible:
    for func in funcs:
        log.info(f"Applying '{func.__name__}' to '{bible.name}'")
        try:
            bible = func(bible)
        except Exception as e:
            log.error(f"'{func.__name__}': {e}")
    return bible
        

def main(args=None):
    log = logging.getLogger(__name__ + ".main")
    if args is None:
        args = ARG_PARSER.parse_args()
        
    args.sources = [ s.lower() for s in args.source ]
    if "list" in args.sources:
        _print_list()
        sys.exit(1)
    # convert the sources:
    sources = []
    src_is_url = []
    src_funcs = []
    for source in args.sources:
        try:
            is_idx, source, funcs = parse_source(source)
        except SourceParseError:
            log.error("Unable to parse source")
            sys.exit(1)
        except KeyError as e:
            log.error(f"Function '{e.args[0]}' is not defined")
            sys.exit(1)
        
        if is_idx:
            # make sure it's in range
            try:
                src = list(DEFAULT_EXTRACTOR.extractors.keys())[int(source)]
            except IndexError:
                log.error(f"Source {src} is out of range")
                sys.exit(1)
            is_url = True
        elif path.isfile(source):
            is_url = False
            src = source
        else:
            # treat it as a URL
            is_url = True
            src = source
        
        if is_url:
            log.info(f"Source '{source}' is '{src}'")
        else:
            log.info(f"Treating '{source}' as file")
            
        sources.append(src)
        src_is_url.append(is_url)
        src_funcs.append(funcs)
        
    if path.exists(args.output) and args.output != "/dev/null":
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
        
    result = None
    stats = []
    for is_url, source, funcs in zip(src_is_url, sources, src_funcs):
        if is_url:
            bible = extract(source)
        else:
            with open(source, "r") as json_file:
                bible = Bible.from_dict(json.load(json_file))
        bible = _apply_funcs(log, funcs, bible)
        stats.append(get_bible_stats(bible).to_dict())
        if result is not None:
            result = merge(result, bible)
        else:
            result = bible
    if len(sources) > 1:
        stats.append(get_bible_stats(result).to_dict())
        
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
    # output stats
    if args.stats is not None:
        with open(args.stats, "w") as stats_file:
            json.dump(stats, stats_file, indent=4)
