'''
Created on 23.08.2017

@author: falensaa
'''

import logging

import imsnpars.nparser.network
import imsnpars.nparser.features
import imsnpars.nparser.trans.builder as tbuilder
import imsnpars.nparser.trans.labeler as tlabeler
import imsnpars.nparser.graph.builder as gbuilder
import imsnpars.nparser.graph.features as gfeatures
import imsnpars.nparser.labels.task as ltask

def buildGraphLabeler(opts, dummyBuilder, reprBuilder):
    reprDim = reprBuilder.getDim()
    
    # parse features
    tokExtractors, featBuilders = gbuilder.buildGraphFeatureExtractors(opts.graphLabelerFeats, reprDim)
    extractor = gfeatures.GraphFeatureExtractor(tokExtractors)
    
    featIds = extractor.getFeatIds() + [ feat.getFeatId() for feat in featBuilders.values() ]
    
    # all network's parameters
    lblNetwork = imsnpars.nparser.network.ParserNetwork(opts.mlpHiddenDim, opts.nonLinFun, featIds)
    featBuilder = imsnpars.nparser.features.FeatReprBuilder(extractor, featBuilders, dummyBuilder, lblNetwork, opts.lblLayer)
    labelerTask = ltask.LabelerGraphTask(featBuilder, lblNetwork, opts.lblLayer)
    return labelerTask
    