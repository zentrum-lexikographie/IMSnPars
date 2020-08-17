import argparse
import itertools
import multiprocessing
import sys

import click
import conllu
import imsnpars.nparser.options as parser_options
import imsnpars.tools.utils as parser_utils
from imsnpars.nparser import builder as parser_builder
from imsnpars.tools.utils import ConLLToken as IMSConllToken


class Parser(object):
    def __init__(self, args, options):
        self.args = args
        self.options = options
        self.instance = None

    def __call__(self, sentence):
        if not self.instance:
            self.instance = parser_builder.buildParser(self.options)
            self.instance.load(self.args.model)
        parser = self.instance
        parser._NDependencyParser__renewNetwork()
        parse_tree = parser._NDependencyParser__predict_tree(
            parser._NDependencyParser__reprBuilder.buildInstance(
                [IMSConllToken(
                    tokId=(i + 1),
                    orth=token['form'],
                    lemma=token['lemma'],
                    pos=token['xpostag'],
                    langPos=token['xpostag'],
                    morph='',
                    headId=None,
                    dep=None,
                    norm=parser_builder.buildNormalizer(self.options.normalize)
                ) for i, token in enumerate(sentence)]
            )
        )
        for pos, token in enumerate(sentence):
            token.update(
                head=parse_tree.getHead(pos) + 1,
                deprel=parse_tree.getLabel(pos)
            )
        return sentence


def build_parser_from_args(cmd_args, parser, model):
    argParser = argparse.ArgumentParser(description="""IMS BiLSTM Parser""", add_help=False)
    argParser.add_argument("--parser", help="which parser to use", choices=["GRAPH", "TRANS"], required=True)
    argParser.add_argument("--normalize", help="normalize the words", type=bool, default=True)
    argParser.add_argument("--model", help="load model from the file", type=str, required=True)
    # parse the second time to get all the args
    parser_options.addParserCmdArguments(parser, argParser)
    args, _ = argParser.parse_known_args(cmd_args)

    opts = parser_utils.NParserOptions()
    parser_options.fillParserOptions(args, opts)
    opts.load(model + ".args")
    opts.logOptions()

    return args, opts


@click.command()
@click.option('-b', '--batch', default=1000, type=int)
@click.option('-i', '--input', default='-', type=click.File('r'))
@click.option('-o', '--output', default='-', type=click.File('w'))
@click.option('-m', '--model', type=str)
@click.option('-p', '--parser', default="TRANS", type=str)
@click.option('-j', '--jobs', default=1, type=int)
def main(input, output, batch, model, parser, jobs):
    args = sys.argv[1:] + ["--normalize", "True", "--parser", parser, "--model", model]
    args, options = build_parser_from_args(cmd_args=args, parser=parser, model=model)
    parser = Parser(args, options)

    # We provide the field definition explicitly, so the parser does not seek
    # through the input stream, looking for a field declaration. The latter
    # will fail on piped stdin.
    sentences = conllu.parse_incr(input, fields=conllu.parser.DEFAULT_FIELDS)
    with multiprocessing.Pool(jobs) as p:
        while True:
            chunk = list(itertools.islice(sentences, batch))
            if len(chunk) == 0:
                break
            for sentence in p.map(parser, chunk):
                output.write(sentence.serialize())


if __name__ == '__main__':
    main()
