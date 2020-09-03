"Tests parser."

from pathlib import Path

import itertools

import conllu

from imsnpars.configure import create_parser, parse


data_dir = (Path(__file__) / '..' / '..' / 'data').resolve()


def test_trans_parser():
    parser = create_parser(data_dir / 'model')
    with (data_dir / 'test.conllu').open() as f:
        sentences = conllu.parse_incr(f, fields=conllu.parser.DEFAULT_FIELDS)
        for sentence in itertools.islice(sentences, 0, 100):
            parse(parser, sentence)
