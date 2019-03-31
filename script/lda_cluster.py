# -*- coding: utf-8 -*-

import os
import argparse

import numpy as np
import scipy.cluster.hierarchy

from analysis_const import Const


def clustering(vectors):
    # Method 'ward' requires the distance metric to be Euclidean
    linkage_mat = scipy.cluster.hierarchy.linkage(
        vectors, method='ward', metric='euclidean')
    return linkage_mat


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('matrix_file',
                        help='input document_topics matrix file')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')
    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    vectors = np.loadtxt(conf.matrix_file, delimiter=',')
    linkage_mat = clustering(vectors)
    
    np.savetxt(os.path.join(conf.out_dir, Const.LINKAGE_MAT_FNAME),
               linkage_mat, delimiter=Const.LINKAGE_MAT_DELIMITER)
