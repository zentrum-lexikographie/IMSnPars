#!/usr/bin/python3

import multiprocessing
from typing import List

from pyconll.unit.sentence import Sentence

from imsnpars.nparser import builder
from imsnpars.tools.utils import ConLLToken as IMSConllToken

parsers = {}


def chunks(lst, n):
    """Yield successive n-sized chunks from lst.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def convert_pyconll_to_imsnpars_sentence(sentence: Sentence, normalizer=None) -> List[IMSConllToken]:
    """Converts token-wise into imsnpars token format.
    """
    sentence_ims = []
    for token_i, token in enumerate(sentence):
        sentence_ims.append(
            IMSConllToken(tokId=token_i + 1,
                          orth=token.form,
                          lemma=token.lemma,
                          pos=token.xpos,
                          langPos=token.xpos,
                          morph="",
                          headId=None,
                          dep=None,
                          norm=normalizer.norm(token.form) if normalizer else None))
    return sentence_ims


def parse_sentence(parser, sentence):
    """Predicts dependencies for a single sentence.

    Resets neural dependency parser, predicts the dependency tree, and adds predictions to input sentence.
    """
    parser._NDependencyParser__renewNetwork()
    instance = parser._NDependencyParser__reprBuilder.buildInstance(sentence)
    tree = parser._NDependencyParser__predict_tree(instance)
    for pos, tok in enumerate(sentence):
        tok.setHeadPos(tree.getHead(pos))
        tok.dep = tree.getLabel(pos)
    return sentence


def parse_document(parser, doc, use_normalizer=False):
    """Iterates over pyconll document and predicts dependencies per sentence.
    """
    normalizer = builder.buildNormalizer(use_normalizer)
    for sent in doc:
        sent_parsed = parse_sentence(parser, convert_pyconll_to_imsnpars_sentence(sent, normalizer))
        for tok, tok_parsed in zip(sent, sent_parsed):
            tok.head = str(tok_parsed.headId)
            tok.deprel = str(tok_parsed.dep)
    return doc


def get_parser(args, options):
    """Manages multiple parser instances and either creates parser or reuses it.
    """
    global parsers
    pid = multiprocessing.current_process().name
    if pid in parsers:
        print("load parser from memory", pid)
        return parsers[pid]
    else:
        print("build and load new parser", pid)
        parser = builder.buildParser(options)
        parser.load(args.model)
        parsers[pid] = parser
        return parser
