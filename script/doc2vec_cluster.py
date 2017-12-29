# -*- coding: utf-8 -*-

'''
doc2vec clustering.
'''

import os
import argparse

import numpy as np
import scipy.cluster.hierarchy
import scipy.spatial.distance
from gensim import models
from gensim.models.doc2vec import LabeledSentence

from analysis_const_draft import ConstDraft
from analysis_const import Const
import analysis_common as common


def clustering(model, vectors):

    #y = scipy.spatial.distance.pdist(vectors, 'cosine')
    y = compute_pdist(model, vectors)
    linkage_mat = scipy.cluster.hierarchy.linkage(y, method='ward')

    # Method 'ward' requires the distance metric to be Euclidean
    #linkage_mat = scipy.cluster.hierarchy.linkage(
    #    vectors, method='ward', metric='euclidean')

    return linkage_mat


def compute_pdist(model, vectors):
    pdist =[]
    n = len(vectors)
    for j in range(n-1):
        for i in range(j+1, n):
            pdist.append(1.0 - model.docvecs.similarity(i, j))
    return pdist
    

def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model-file', '-m', default=None,
                        help="input model file")
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    model_file = resolve_io_path(
        conf, conf.model_file, ConstDraft.DOC2VEC_MODEL_FNAME)
    model = models.Doc2Vec.load(model_file)

    vectors = [model.docvecs[i]  for i in range(len(model.docvecs))]

    linkage_mat = clustering(model, vectors)
    
    np.savetxt(os.path.join(conf.out_dir, Const.LINKAGE_MAT_FNAME),
               linkage_mat, delimiter=Const.LINKAGE_MAT_DELIMITER)
