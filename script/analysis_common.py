# -*- coding: utf-8 -*-

import os
import re

from analysis_const import Const


def read_labels(labels_file):
    lines = []
    with open(labels_file) as fl:
        for line in fl:
            lines.append(line.strip())
    return lines


class SourcePartInfo:

    def __init__(self, index, path, tag, begin_line_num, end_line_num):
        self.index = index
        self.path = path
        self.tag = tag  # function name
        self.begin_line_num = begin_line_num
        self.end_line_num = end_line_num

    def __str__(self):
        return '[%d] %s, %s:%d-%d' % (
            self.index, self.tag, self.path,
            self.begin_line_num, self.end_line_num)

    def make_dict(self):
        return dict(vars(self))

    @classmethod
    def from_dict(cls, dic):
        return cls(int(dic['index']),
                   dic['path'],
                   dic['tag'],
                   int(dic['begin_line_num']),
                   int(dic['end_line_num']))

    @classmethod
    def from_label(cls, index, label):
        fields = label.split(Const.LABEL_FIELD_DELIMITER)
        return cls(index=index,
                   path=fields[0],
                   tag=fields[1],
                   begin_line_num=int(fields[2]),
                   end_line_num=int(fields[3]))


class SourceAccessor:

    def __init__(self, info_list=None, root_dir=None):
        if info_list is None:
            self._info_dic = dict()
        else:
            self._info_dic = {info.index: info for info in info_list}
        self._root_dir = root_dir
        self._file_cache = {}

    @classmethod
    def create_empty(cls, root_dir):
        return cls(None, root_dir)
        
    @classmethod
    def from_labels(cls, labels, root_dir=None):
        info_list = [SourcePartInfo.from_label(i, l) for i, l in enumerate(labels)]
        return cls(info_list, root_dir)

    def get_info(self, index):
        return self._info_dic[index]

    def content_accessible(self):
        return self._root_dir is not None
    
    def get_content(self, index):
        info = self._info_dic[index]
        
        if not index in self._file_cache:
            self._file_cache[index] = self._read_lines(info)
            
        lines = self._file_cache[index]
        return ''.join(lines[info.begin_line_num-1:info.end_line_num])

    def get_content_by_info(self, info):
        if not info.index in self._info_dic:
            self._info_dic[info.index] = info
        return self.get_content(info.index)

    def _read_lines(self, info):
        file_path = os.path.join(self._root_dir, info.path)
        with open(file_path, encoding=Const.SOURCE_ENCODING) as fl:
            return fl.readlines()


class ClusterNode:
    
    def __init__(self, index, distance=0, represent=1, child1=None, child2=None):
        self.index = index
        self.distance = distance
        self.represent = represent
        self.child1 = child1
        self.child2 = child2
        
    def __str__(self):
        if self.represent == 1:
            return '[%d]' %(self.index)
        return '[%d] distance=%.3f represent=%d' %(
            self.index, self.distance, self.represent)

    @classmethod
    def build_hierarchy(cls, linkage_mat):
        nodes = cls.build_linkage_nodes(linkage_mat)
        return nodes[-1]
        
    @classmethod
    def build_linkage_nodes(cls, linkage_mat):
        
        # linkage_mat[i] : index_a, index_b, distance, represent
        #                  [i][0],  [i][1],  [i][2],   [i][3]

        num_leaves = int(linkage_mat[-1][3])
        nodes = [cls(i) for i in range(num_leaves)]
        
        index = num_leaves
        for a, b, distance, represent in linkage_mat:
            a, b, represent = int(a), int(b), int(represent)
            c = cls(index, distance, represent, nodes[a], nodes[b])
            nodes.append(c)
            index += 1

        return nodes
        
    def collect_by_distance(self, distance, nodes=None):
        if nodes is None:
            nodes = []
        if self.distance <= distance:
            nodes.append(self)
        else:
            self.child1.collect_by_distance(distance, nodes)
            self.child2.collect_by_distance(distance, nodes)
        return nodes
    
    def collect_leaves(self, nodes=None):
        if nodes is None:
            nodes = []
        if self.represent == 1:
            nodes.append(self)
        else:
            self.child1.collect_leaves(nodes)
            self.child2.collect_leaves(nodes)
        return nodes
