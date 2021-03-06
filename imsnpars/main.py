'''
Created on 18.08.2017

@author: falensaa
'''

import logging
import sys
import random
import argparse

from .tools import utils, evaluator, training
from .nparser import builder
from .nparser import options

def buildParserFromArgs():
    argParser = argparse.ArgumentParser(description="""IMS Neural Parser""", add_help=False)
    
    parserArgs = argParser.add_argument_group('parser')
    parserArgs.add_argument("--parser", help="which parser to use", choices=[ "GRAPH", "TRANS" ], required=True)
    parserArgs.add_argument("--loglevel", help="which log level to use", choices=[ "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL" ], required=False, default="DEBUG")
    
    # files
    filesArgs = argParser.add_argument_group('files')
    filesArgs.add_argument("--train", help="training file", type=str, required=False)
    filesArgs.add_argument("--dev", help="development file", type=str, required=False)
    filesArgs.add_argument("--model", help="load model from the file", type=str, required=False)
    filesArgs.add_argument("--test", help="test file", type=str, required=False)
    filesArgs.add_argument("--output", help="output predictions to the file", type=str, required=False)
    filesArgs.add_argument("--save", help="save model to the file", type=str, required=False)
    filesArgs.add_argument("--save_max", help="save the best model to the file", type=str, required=False)
    
    # format
    formatArgs = argParser.add_argument_group('format')
    formatArgs.add_argument("--format", help="file format", choices=[ "conll06", "conllu" ], type=str, required=False, default="conllu")
    formatArgs.add_argument("--normalize", help="normalize the words", choices=[ "True", "False" ], type=str, required=False, default="True")
    
    # training
    trainingArgs = argParser.add_argument_group('training')
    trainingArgs.add_argument("--patience", help="patience for the early update", type=int, required=False)
    trainingArgs.add_argument("--seed", help="random seed (different than dynet-seed)", type=int, required=False, default=42)
    trainingArgs.add_argument("--epochs", help="nr of epochs", type=int, required=False, default=30)
    
    # dynet
    dynetArgs = argParser.add_argument_group('dynet')
    dynetArgs.add_argument("--dynet-gpu-ids", help="turns on dynet", required=False)
    dynetArgs.add_argument("--dynet-devices", help="turns on dynet", required=False)
    dynetArgs.add_argument("--dynet-autobatch", help="turns on dynet-autobatch", required=False)
    dynetArgs.add_argument("--dynet-seed", help="sets random seed generator for dynet", required=False)
    
    
    # parse for the first time to only get the parser name
    args, _ = argParser.parse_known_args()
    
    # set logging level
    lformat = '[%(levelname)s] %(asctime)s %(name)s# %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.getLevelName(args.loglevel), format=lformat)
    
    # parse the second time to get all the args
    options.addParserCmdArguments(args.parser, argParser)
    argParser.add_argument('--help', action='help', default=argparse.SUPPRESS, help=argparse._('show this help message and exit'))
    
    args = argParser.parse_args()

    # this still leaves dynet-seed being random
    random.seed(args.seed)
    logging.info("Freezing random seed: %i" % args.seed)

    opts = utils.NParserOptions()
    options.fillParserOptions(args, opts)
    
    if args.model != None:
        # all the args fields will get overwritten
        opts.load(args.model + ".args")
    
    opts.logOptions()
    parser = builder.buildParser(opts)
    
    if args.save != None:
        opts.save(args.save + ".args")
        
    return args, opts, parser
    
def prepareDatasets(args, opts):
    # format reader
    tokenBuilder = utils.buildFormatReader(args.format)
    normalizer =  builder.buildNormalizer(utils.parseBoolean(opts.normalize))
    
    trainData = None
    if args.train:
        trainData = utils.readSentences(args.train, tokenBuilder, normalizer)
    
    devData = None
    if args.dev != None:
        devData = utils.readSentences(args.dev, tokenBuilder, normalizer)
            
    testData = None
    if args.test:
        testData = utils.readSentences(args.test, tokenBuilder, normalizer)
    
    return trainData, devData, testData
            

def main():
    args, opts, parser = buildParserFromArgs()

    if args.test == None and args.output != None:
        logging.warn("Option 'output' will not be used without specifying 'test' file")

    trainData, devData, testData = prepareDatasets(args, opts)
    if args.train:
        if args.save == None and args.save_max == None:
            logging.warn("Training without save option")

        if args.patience:
            trainer = training.EarlyStopTrainingManager(args.epochs, lambda: parser.save(args.save),
                                                        patience=args.patience)
        elif args.save_max != None:
            trainer = training.SaveMaxTrainingManager(args.epochs, lambda: parser.save(args.save),
                                                      lambda: parser.save(args.save_max))
        else:
            trainer = training.AllEpochsTrainingManager(args.epochs, lambda: parser.save(args.save))

        parser.train(trainData, trainer, devData)

        # because of early update we need to load the best model
        if args.patience and args.test != None and args.save != None:
            parser.load(args.save)

    elif args.model != None:
        parser.load(args.model)
    else:
        logging.error("One option: train/load is obligatory")
        sys.exit()

    if args.test != None:
        if args.output == None:
            lazyEval = evaluator.LazyTreeEvaluator()
            parser.predict(testData, lazyEval)
            logging.info("Test acc: %f %f" % (lazyEval.calcUAS(), lazyEval.calcLAS()))
        else:
            parser.predict(testData, utils.LazySentenceWriter(open(args.output, "w")))


if __name__ == '__main__':
    main()
