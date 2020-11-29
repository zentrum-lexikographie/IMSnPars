import argparse
from pathlib import Path
import imsnpars.nparser.options as parser_options
import imsnpars.tools.utils as parser_utils
from imsnpars.nparser import builder as parser_builder
from imsnpars.tools.utils import ConLLToken as IMSConllToken
from imsnpars.tools.utils import Normalizer as IMSNormalizer


def create_parser(model_path):
    model = Path(f"{model_path}/model").as_posix()
    argParser = argparse.ArgumentParser(add_help=False)
    argParser.add_argument(
        "--parser", choices=["GRAPH", "TRANS"], required=True
    )
    argParser.add_argument("--normalize", type=bool, default=True)
    argParser.add_argument("--model", type=str, required=True)
    # parse the second time to get all the args
    parser_options.addParserCmdArguments("TRANS", argParser)
    args, _ = argParser.parse_known_args(
        ["--normalize", "True", "--parser", "TRANS", "--model", model]
    )

    opts = parser_utils.NParserOptions()
    parser_options.fillParserOptions(args, opts)
    opts.load(Path(f"{model_path}/model.args").as_posix())

    parser = parser_builder.buildParser(opts)
    parser.load(args.model)
    return parser


normalizer = IMSNormalizer(normalizeNumbers=True, lowercase=True)


def parse(parser, sentence):
    parser._NDependencyParser__renewNetwork()
    parse_tree = parser._NDependencyParser__predict_tree(
        parser._NDependencyParser__reprBuilder.buildInstance(
            [IMSConllToken(
                tokId=(i + 1),
                orth=token['form'],
                lemma=token['lemma'],
                pos=token['xpos'],
                langPos=token['xpos'],
                morph='',
                headId=None,
                dep=None,
                norm=normalizer
            ) for i, token in enumerate(sentence)]
        )
    )
    for pos, token in enumerate(sentence):
        token.update(
            head=parse_tree.getHead(pos) + 1,
            deprel=parse_tree.getLabel(pos)
        )
    return sentence
