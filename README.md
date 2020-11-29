# IMSnPars
IMS Neural Dependency Parser is a re-implementation of the transition- and graph-based parsers described in [Simple and Accurate Dependency Parsing Using Bidirectional LSTM Feature Representations](https://aclweb.org/anthology/Q16-1023)

If you are using this software, please cite the paper [DOI:10.18653/v1/P19-1012](http://doi.org/10.18653/v1/P19-1012) by Agnieszka Faleńska ([github](https://github.com/AgnieszkaFalenska/), [www](https://www.ims.uni-stuttgart.de/en/institute/team/Falenska/)) and Jonas Kuhn ([www](https://www.ims.uni-stuttgart.de/en/institute/team/Kuhn-00013/)).


## Releases

### acl2019 branch
The parser was developed for the paper [The (Non-)Utility of Structural Features in BiLSTM-based
Dependency Parsers](https://www.aclweb.org/anthology/P19-1012) (see [acl2019 branch](https://github.com/AgnieszkaFalenska/IMSnPars/tree/acl2019) for all the paper specific changes and analysis tools):

```
@inproceedings{falenska-kuhn-2019-non,
    title = "The (Non-)Utility of Structural Features in {B}i{LSTM}-based Dependency Parsers",
    author = "Falenska, Agnieszka  and Kuhn, Jonas",
    booktitle = "Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/P19-1012",
    doi = "10.18653/v1/P19-1012",
    pages = "117--128",
}
```


## Usage

### Install virtual env

```sh
python3.6 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --use-feature=2020-resolver
pip install -r requirements-dev.txt --use-feature=2020-resolver
python setup.py develop -q
```

### Download training data and serialized model
Please contact the System Administrator for an user account.

```sh
# initialize DVC in git repo
# dvc init

# set the DVC endpoint
dvc remote add imsnpars-data ssh://odo.dwds.de/home/imsnpars/v1

# configure your creds (You SSH username/password on odo.dwds.de)
dvc remote modify --local imsnpars-data port 22
dvc remote modify --local imsnpars-data user YOURNAME
dvc remote modify --local imsnpars-data password TOPSECRETPW

# dowload data
dvc pull -r imsnpars-data
```

### Training a new Model
There are two types of dependency parsers available
that need to be specified with the `--parser` flag:

- **Transition-based parser** (`TRANS`)
- **Graph-based parser** (`GRAPH`)

The training set must be `.conllu` file, 
and its path is specified with the `--train` flag.
Further a file path must be specified with the `--save` flag
where to store the trained and serialized model.

```sh
imsnparser.py \
    --parser [TRANS or GRAPH] \
    --train [train_file] \
    --save [model_file]
```

Example, given you [downloaded the HDT treebank dataset](#download-training-data-and-serialized-model) mentionend above,
we train a new model with the transition-based parser (TRANS):

```sh
imsnparser.py \
    --parser TRANS \
    --train=data/hdt/train.conllu  \
    --save=data/model/my-new-model-v1.2.3
```

### Inference with a Pre-trained Model
For evaluation as well as production purposes, 
we can load a pre-trained model as explained in the [previous chapter](#training-a-new-model).
Both input data (`--test`) and output data (`--output`) are `.conllu` files.

```sh
imsnparser.py \
    --parser [TRANS or GRAPH] \
    --model [model_file] \
    --test [test_file] \
    --output [output_file]
```

Analogous to the previous example,
we can run inference on the HDT test set with our pre-trained model:

```sh
mkdir -p data/output
imsnparser.py \
    --parser TRANS \
    --model=data/model/my-new-model-v1.2.3 \
    --test=data/hdt/test.conllu  \
    --output=data/output/predicted.conllu
```

### Other settings
The parser supports many other options. All of them can be seen after running:
```sh
imsnparser.py --parser TRANS --help
imsnparser.py --parser GRAPH --help
```


### Tests
*IMSnPars* comes with four testing scripts to check if everything works fine:
1. `systests/test_trans_parser.sh` -- trains a new transition-based parser on small fake data and uses this model for prediction
2. `systests/test_graph_parser.sh` -- trains a new graph-based parser on small fake data and uses this model for prediction
3. `systests/test_all_trans_parsers.sh` -- trains multiple transition-based models with different sets of options
4. `systests/test_all_graph_parsers.sh` -- trains multiple graph-based models with different sets of options

Please make sure that the software is installed as python package, e.g. run `python setup.py develop -q`.

We recommend running the two first scripts before using *IMSnPars* for other purposes (both tests take less than a minute). Both of the scripts should end with an information that everything went fine. Transition-based parser achieves LAS=64.61 on the fake data and the graph-based one LAS=66.47.
