#!/bin/bash

# options
D=$(dirname $0)
source "${D}/get_global_vars.sh"

TRAIN="${D}/test_data/train.conllu"
DEV="${D}/test_data/dev.conllu"

OUT="${D}/out-graph"
mkdir -p "${OUT}"

MODEL="${OUT}/test_graph.model"
DEVICE="CPU"

PARSER=imsnparser.py

# training
echo "Training"
$PARSER \
        --dynet-devices $DEVICE \
        --dynet-seed $DYNET_SEED \
        --seed $PARS_SEED \
        --loglevel DEBUG \
        --parser GRAPH \
        --train $TRAIN \
    	--save $MODEL \
    	--dev $DEV \
    	--format conllu \
    	--epochs 2 \
    	--test $DEV \
		--contextRepr bilstm \
        --representations word,pos \
        --labeler "graph-mtl" \
        --output $MODEL.train.out
    	
echo "Predicting"
$PARSER \
        --dynet-devices "CPU" \
        --dynet-seed 42 \
        --model $MODEL \
        --parser GRAPH \
        --format conllu \
        --test $DEV \
    	--output $MODEL.predict.out
    	
echo "Comparing"
diff $MODEL.train.out $MODEL.predict.out > $MODEL.train.diff
echo "OK"
