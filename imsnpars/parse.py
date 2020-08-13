#!/usr/bin/python3

import argparse
import logging
import multiprocessing
import os
import sys
from glob import glob
from pathlib import Path

import pyconll

import imsnpars.nparser.options as options
import imsnpars.tools.utils as utils
# Set for graph search in parser
from imsnpars.zdl.utils import get_parser, parse_document, chunks

# Set recursion level because of networkx exception
sys.setrecursionlimit(200)

lformat = '[%(levelname)s] %(asctime)s %(name)s# %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=lformat)


# TODO refactor parser generation - too complicated right now
def build_parser_from_args(cmd_args=None):
    argParser = argparse.ArgumentParser(description="""IMS BiLSTM Parser""", add_help=False)

    parserArgs = argParser.add_argument_group('parser')
    parserArgs.add_argument("--parser", help="which parser to use", choices=["GRAPH", "TRANS"], required=True)
    parserArgs.add_argument("--jobs", help="", type=int, default=1)
    parserArgs.add_argument("--normalize", help="normalize the words", type=bool, required=False, default=True)

    # files
    filesArgs = argParser.add_argument_group('files')
    filesArgs.add_argument("--src", help="source file", type=str, required=True)
    filesArgs.add_argument("--conll", help="outputs conll formatted files", action="store_true", required=False)
    filesArgs.add_argument("--dest", help="source file destination", type=str, required=True)
    filesArgs.add_argument("--model", help="load model from the file", type=str, required=True)

    # parse for the first time to only get the parser name
    args, _ = argParser.parse_known_args(cmd_args)

    # parse the second time to get all the args
    options.addParserCmdArguments(args.parser, argParser)
    args = argParser.parse_args(cmd_args)

    opts = utils.NParserOptions()
    options.fillParserOptions(args, opts)
    opts.load(args.model + ".args")
    opts.logOptions()

    return args, opts


def process_files_parallel(srcs, args, options):
    """Parses conllu files.

    Predictions are either stored into separate files (when destination is given) or printed to console.
    """
    parser = get_parser(args, options)
    for src_i, src in enumerate(srcs):
        doc = pyconll.load_from_file(src)
        file_name = os.path.basename(src)
        if args.conll:
            file_name = file_name[:-len("tabs")] + "conllu"
        tgt_path = Path(os.path.join(args.dest, doc[0].meta_value("DDC:meta.collection"), file_name))
        if not tgt_path.exists() or (os.path.getmtime(tgt_path) < os.path.getmtime(src)):
            parse_document(parser, doc, options.normalize)
            logging.info("({}) - parsed document".format(doc[0].meta_value("DDC:meta.basename")))
            if not tgt_path.parent.exists():
                tgt_path.parent.mkdir(parents=True)
            with open(tgt_path, 'w') as fh:
                fh.write(doc.conll())
        else:
            logging.info("({}) - SKIP - parsed document up-to-date".format(tgt_path))


def main():
    args, options = build_parser_from_args()
    src_files = glob(args.src, recursive=True)
    if len(src_files) == 0:
        raise FileNotFoundError("No files found for parsing!")
    files = [(src, args, options) for src in chunks(src_files, 25)]
    logging.info("Create MPPool with #njobs: {}".format(args.jobs))
    with multiprocessing.Pool(args.jobs) as pool:
        pool.starmap(process_files_parallel, files, chunksize=10)


if __name__ == '__main__':
    main()
