# -*- coding: utf-8 -*-

'''
make dendrogram from linkege_mat.csv
'''

import os
import re
import argparse
import pickle

import numpy as np
import scipy.cluster.hierarchy
import matplotlib.pyplot as plt

from analysis_const import Const
import analysis_common as common


# linkage_mat[i] : index_a, index_b, distance, represent
#                  [i][0],  [i][1],  [i][2],   [i][3]


def write_dendrogram(out_file, linkage_mat, info_accessor, similar_distance):
    plt.figure(figsize=(20, 48), dpi=100)

    num_singleton = int(linkage_mat[-1][3])

    def color_func(k):
        a, b, distance, represent = linkage_mat[k - num_singleton]
        return 'red' if distance <= similar_distance else 'gray'

    def label_func(k):
        info = info_accessor.get_info(k)
        return '%s@%s:%d-%d' % (
            info.tag, info.path, info.begin_line_num, info.end_line_num)

    scipy.cluster.hierarchy.dendrogram(
        linkage_mat,
        #labels=labels,
        #p=10, truncate_mode='level',
        orientation='right',
        leaf_font_size=8,
        distance_sort=True,
        show_leaf_counts=True,
        leaf_label_func=label_func,
        link_color_func=color_func)

    plt.tight_layout()
    plt.savefig(out_file)


def resolve_similar_distance(linkage_mat, num_of_linkages):
    index = min(num_of_linkages - 1, len(linkage_mat)-1)
    return linkage_mat[index][2]


def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--labels-file', '-l', default=None,
                        help="input labels file")
    parser.add_argument('--linkage-file', default=None,
                        help="input linkage file")
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help="output dir")
    parser.add_argument('--num-of-linkages', type=int,
                        default=Const.DEFAULT_NUM_OF_LINKAGES,
                        help='number of linkages')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    labels_file = resolve_io_path(conf, conf.labels_file, Const.LABELS_FNAME)
    labels = common.read_labels(labels_file)
    info_accessor = common.SourceAccessor.from_labels(labels)

    linkage_file = resolve_io_path(conf, conf.linkage_file, Const.LINKAGE_MAT_FNAME)
    linkage_mat = np.loadtxt(linkage_file, delimiter=Const.LINKAGE_MAT_DELIMITER)

    similar_distance = resolve_similar_distance(linkage_mat, conf.num_of_linkages)
    
    dendro_file = os.path.join(conf.out_dir, Const.DENDROGRAM_FNAME)
    write_dendrogram(dendro_file, linkage_mat, info_accessor, similar_distance)
