# -*- coding: utf-8 -*-

'''
Doc2Vec query
'''

import os
import re
import argparse

from gensim import models
from gensim.models.doc2vec import LabeledSentence

from doc2vec_common import Doc2VecConst
from analysis_const import Const
import analysis_common as common


def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)

        
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model-file', '-m', default=None,
                        help="input model file")
    parser.add_argument('--query-index', '-q', type=int, default=0,
                        help='query index')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    model_file = resolve_io_path(
        conf, conf.model_file, Doc2VecConst.MODEL_FNAME)
    model = models.Doc2Vec.load(conf.model_file)

    #vector = model.docvecs[conf.query_index]
    #print('vector: ')
    #print(vector)

    print('# query index %d:' % conf.query_index)
    print(model.docvecs.index_to_doctag(conf.query_index))

    print('# similar:')
    results = model.docvecs.most_similar(conf.query_index, topn=10)
    for label, score in results:
        print('%s\t%f' % (label, score))
