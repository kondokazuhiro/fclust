# -*- coding: utf-8 -*-

'''
Train with Doc2Vec
'''

import os
import re
import argparse

from gensim import models
from gensim.models.doc2vec import LabeledSentence

from analysis_const_draft import ConstDraft
from analysis_const import Const
import analysis_common as common


def read_docs_as_matrix(docs_file):
    docs = []
    with open(docs_file) as fl:
        for line in fl:
            words = re.split(r'\s+', line.strip())
            docs.append(words)
    return docs


def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def create_model(sentences):
    # https://radimrehurek.com/gensim/models/doc2vec.html
    # - size is the dimensionality of the feature vectors.
    # - min_count = ignore all words with total frequency lower than this.
    # - iter = number of iterations (epochs) over the corpus.
    #   The default inherited from Word2Vec is 5, but values of 10 or 20 are
    #   common in published 'Paragraph Vector’ experiments.
    # - dm defines the training algorithm. By default (dm=1),
    #   'distributed memory’ (PV-DM) is used.
    #   Otherwise, distributed bag of words (PV-DBOW) is employed.

    # https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb
    model = models.Doc2Vec(size=50, min_count=1, iter=55)
    model.build_vocab(sentences)

    return model


def train_model(mode, sentences):
    print('begin train')

    # https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)

        
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--labels-file', '-l', default=None,
                        help="input labels file")
    parser.add_argument('--model-file', '-m', default=None,
                        help="input model file")
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    docs_file = resolve_io_path(conf, conf.docs_file, Const.DOCS_FNAME)
    docs = read_docs_as_matrix(docs_file)
                             
    labels_file = resolve_io_path(conf, conf.labels_file, Const.LABELS_FNAME)
    labels = common.read_labels(labels_file)

    sentences = []
    for words, label in zip(docs, labels):
        sentences.append(LabeledSentence(words=words, tags=[label]))

    if conf.model_file is not None:
        model = models.Doc2Vec.load(conf.model_file)
    else:
        model = create_model(sentences)

    train_model(model, sentences)
    
    model.save(os.path.join(conf.out_dir, ConstDraft.DOC2VEC_MODEL_FNAME))
