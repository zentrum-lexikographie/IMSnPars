'''
Created on 23.08.2017

@author: falensaa
'''

from imsnpars.tools import  utils

def addParserCmdArguments(argParser):
    transArgs = argParser.add_argument_group('Transition-based parser')
    
    # trans system
    transArgs.add_argument("--system", help="transition system", choices=[ "ArcHybrid", "ArcStandard", "ASSwap", "ArcHybridWithSwap" ], required=False, default="ASSwap")
    transArgs.add_argument("--oracle", help="oracle algorithm", choices=[ "static", "dynamic", "lazy", "eager" ], required=False, default="lazy")
    transArgs.add_argument("--features", help="transition-based features", required=False, default="s0,s1,b0")
                
    # options for dynamic oracle
    transArgs.add_argument("--aggresive", help="aggresive exploration for the dynamic oracle", choices=[ "True", "False" ], required=False, default="True")

def fillParserOptions(args, opts):
    # transition system
    opts.system = args.system
    opts.features = args.features.split(",")
            
    # oracle
    opts.pagg = 0.1
    opts.oracle = args.oracle
    opts.aggresive = utils.parseBoolean(args.aggresive)
    
    return opts
