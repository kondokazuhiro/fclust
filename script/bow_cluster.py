# -*- coding: utf-8 -*-

'''
BOW clustering.
'''

import os
import argparse

import numpy as np
import scipy.cluster.hierarchy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from analysis_const import Const
import analysis_common as common


def clustering(vectors):
    
    # Method 'ward' requires the distance metric to be Euclidean
    linkage_mat = scipy.cluster.hierarchy.linkage(
        vectors, method='ward', metric='euclidean')

    return linkage_mat


def normalize(np_vectors):
    vmax = np_vectors.max()
    vmin = np_vectors.min()
    return (np_vectors - vmin).astype(float) / (vmax - vmin).astype(float)


def docs_to_vectors(docs, tfidf):
    if tfidf:
        vectorizer = TfidfVectorizer(use_idf=True, token_pattern=r'[^\s]+')
        sp_vectors = vectorizer.fit_transform(docs)
        vectors = sp_vectors.toarray()
    else:
        vectorizer = CountVectorizer(token_pattern=r'[^\s]+')
        sp_vectors = vectorizer.fit_transform(docs)
        vectors = normalize(sp_vectors.toarray())

    return vectors
    

def read_lines(in_file):
    lines = []
    with open(in_file) as fl:
        for line in fl:
            lines.append(line.strip())
    return lines


def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')
    parser.add_argument('--tfidf', action='store_true', default=False,
                        help='apply TF/IDF')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    docs_file = resolve_io_path(conf, conf.docs_file, Const.DOCS_FNAME)
    docs = np.array(read_lines(docs_file))

    vectors = docs_to_vectors(docs, conf.tfidf)

    linkage_mat = clustering(vectors)
    
    np.savetxt(os.path.join(conf.out_dir, Const.LINKAGE_MAT_FNAME),
               linkage_mat, delimiter=Const.LINKAGE_MAT_DELIMITER)
