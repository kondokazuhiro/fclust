# -*- coding: utf-8 -*-

'''
resolve similar functions in clustering result.
'''

import os
import re
import argparse
import pickle

import numpy as np

from analysis_const import Const
import analysis_common as common


def make_similar_data(root_node, similar_distance, info_accessor):
    nodes = root_node.collect_by_distance(similar_distance)
    nodes = [nd for nd in nodes if nd.represent > 1]
    nodes.sort(key=lambda c: c.distance)

    data = {
        'distance_threshold': similar_distance,
        'clusters': []
    }
    for node in nodes:
        cluster = {
            'index': node.index,
            'distance': node.distance,
            'represent': node.represent,
            'elements': [],
        }
        data['clusters'].append(cluster)

        for leaf in node.collect_leaves():
            info = info_accessor.get_info(leaf.index)
            cluster['elements'].append(info.make_dict())
    return data


def distance_by_nclusters(linkage_mat, num_of_clusters):
    # linkage_mat[i] ::= cluster_a, cluster_b, distance, represent
    #                    [i][0],    [i][1],    [i][2],   [i][3]
    link_len = len(linkage_mat)
    if link_len < num_of_clusters:
        return linkage_mat[0][2]
    return linkage_mat[link_len - num_of_clusters][2]


def distance_by_nlinkages(linkage_mat, num_of_linkages):
    index = min(num_of_linkages - 1, len(linkage_mat)-1)
    return linkage_mat[index][2]


def resolve_similar_distance(linkage_mat, conf):
    if conf.num_of_linkages is not None:
        return distance_by_nlinkages(linkage_mat, conf.num_of_linkages)
    return distance_by_nclusters(linkage_mat, conf.num_of_clusters)


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

    cls_group = parser.add_mutually_exclusive_group(required=False)
    cls_group.add_argument('--num-of-clusters', type=int,
                           default=Const.DEFAULT_NUM_OF_CLUSTERS,
                           help='number of clusters')
    cls_group.add_argument('--num-of-linkages', type=int,
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

    distance = resolve_similar_distance(linkage_mat, conf)

    root_node = common.ClusterNode.build_hierarchy(linkage_mat)

    similar_data = make_similar_data(root_node, distance, info_accessor)
    similar_file = os.path.join(conf.out_dir, Const.SIMILAR_PKL_FNAME)
    with open(similar_file, 'wb') as fl:
        pickle.dump(similar_data, fl)
