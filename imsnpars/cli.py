import logging
from pathlib import Path
import sys

import boltons.iterutils
import click
import conllu
import psutil
import ray

from imsnpars.configure import create_parser, parse

logging.basicConfig(stream=sys.stderr, level=logging.WARN)


@ray.remote(num_cpus=1)
class Parser:
    def __init__(self, model_path):
        self.parser = create_parser(Path(model_path))

    def parse(self, sentences):
        return [parse(self.parser, s) for s in sentences]


@click.command()
@click.option('-i', '--input', default='-', type=click.File('r'))
@click.option('-o', '--output', default='-', type=click.File('w'))
@click.option('-b', '--batch-size', type=int, default=10)
@click.option('-m', '--model', type=str, required=True)
def main(input, output, model, batch_size):
    ray.init(
        include_dashboard=False,
        configure_logging=False
    )

    parsers = ray.util.ActorPool(
        [Parser.remote(model) for _ in range(psutil.cpu_count())]
    )
    sentences = conllu.parse_incr(input, fields=conllu.parser.DEFAULT_FIELDS)
    batches = boltons.iterutils.chunked_iter(sentences, batch_size)

    for batch in parsers.map(lambda p, b: p.parse.remote(b), batches):
        for sentence in batch:
            output.write(sentence.serialize())


if __name__ == '__main__':
    main()
