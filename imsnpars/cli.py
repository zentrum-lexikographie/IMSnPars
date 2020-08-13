import click
import conllu
import itertools
import multiprocessing

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
                    pos=token['xpos'], langPos=token['xpos'],
                    morph='',
                    headId=None,
                    dep=None,
                    norm=None  # FIXME: normalize tokens?
                ) for i, token in sentence]
            )
        )
        for pos, token in enumerate(sentence):
            token.update(
                head=parse_tree.getHead(pos),
                deprel=parse_tree.getLabel(pos)
            )
        return sentence


def parser_stub(sentence):
    return sentence


@click.command()
@click.option('-b', '--batch', default=1000, type=int)
@click.option('-i', '--input', default='-', type=click.File('r'))
@click.option('-o', '--output', default='-', type=click.File('w'))
def main(input, output, batch):
    # FIXME: translate CLI args, options into parser parameters
    # parser = Parser(None, None)
    parser = parser_stub

    # We provide the field definition explicitly, so the parser does not seek
    # through the input stream, looking for a field declaration. The latter
    # will fail on piped stdin.
    sentences = conllu.parse_incr(input, fields=conllu.parser.DEFAULT_FIELDS)
    with multiprocessing.Pool() as p:
        while True:
            chunk = list(itertools.islice(sentences, batch))
            if len(chunk) == 0:
                break
            for sentence in p.map(parser, chunk):
                output.write(sentence.serialize())


if __name__ == '__main__':
    main()
