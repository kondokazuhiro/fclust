# -*- coding: utf-8 -*-

'''
edit distance clustering.
'''

import os
import re
import argparse

import numpy as np
import scipy.cluster.hierarchy
import edit_distance

from analysis_const import Const
import analysis_common as common


def clustering(pdists):
    return scipy.cluster.hierarchy.linkage(pdists, method='ward')


def compute_pdists_in_docs(docs, length_ratio_threshold=None):
    pdists = []
    n = len(docs)
    for j in range(n-1):
        for i in range(j+1, n):
            len_i = len(docs[i])
            len_j = len(docs[j])
            len_ratio = min(len_i, len_j) / max(len_i, len_j)
            if (length_ratio_threshold is not None
                and len_ratio < length_ratio_threshold):
                ratio = 1.0
            else:
                sm = edit_distance.SequenceMatcher(a=docs[j], b=docs[i])
                ratio = sm.distance() * 2 / (len_j + len_i)
            pdists.append(ratio)
    return pdists


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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')
    parser.add_argument('--length-ratio-threshold', '-r', default=None,
                        type=float, help='length ratio threshold')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    docs_file = resolve_io_path(conf, conf.docs_file, Const.DOCS_FNAME)
    docs = read_docs_as_matrix(docs_file)

    pdists = compute_pdists_in_docs(docs, conf.length_ratio_threshold)
    linkage_mat = clustering(pdists)
    
    np.savetxt(os.path.join(conf.out_dir, Const.LINKAGE_MAT_FNAME),
               linkage_mat, delimiter=Const.LINKAGE_MAT_DELIMITER)
