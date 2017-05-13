# -*- coding: utf-8 -*-

'''
抽出されたタグ情報(ctags-x形式)から、
関数ごとに文書とした文書集合の生成。

ex.
  global -f -d -L list > defs.txt
  global -f -r -L list > refs.txt
  global -f -s -L list > syms.txt
  python tags_to_docs_func.py -d defs.txt -r refs.txt -s syms.txt -o result
'''

import os
import sys
import re
import argparse

from analysis_const import Const


#STOP_WORDS = ['NULL']
STOP_WORDS = []


class Reference:

    def __init__(self, tag, line_num, ref_line):
        self.tag = tag
        self.line_num = line_num
        self.ref_line = ref_line
        self.word = tag

    def __str__(self):
        return '%d:%s' % (self.line_num, self.tag)

    def is_unified(self):
        return self.tag != self.word
    

class Definition:

    def __init__(self, tag, line_num, def_line):
        self.tag = tag
        self.line_num = line_num
        self.def_line = def_line
        self._refs = []

    def __str__(self):
        return 'def:%d:%s' % (self.line_num, self.tag)

    def add_ref(self, ref):
        self._refs.append(ref)

    def commit_refs(self):
        self._refs.sort(key=lambda ref: ref.line_num)
        
    def get_refs(self):
        return self._refs

    def num_refs(self):
        return len(self._refs)

    def tail_line_num(self):
        return self._refs[-1].line_num if len(self._refs) > 0 else self.line_num


class SourceFile:

    def __init__(self, name):
        self.name = name
        self._def_dic = dict()
        self._defs = None

    def add_def(self, tag, line_num, def_line):
        self._def_dic[tag] = Definition(tag, line_num, def_line)

    def commit_defs(self):
        self._defs = sorted(self._def_dic.values(), key=lambda de: de.line_num)

    def add_ref(self, ref):
        for de in reversed(self._defs):
            if de.line_num <= ref.line_num:
                de.add_ref(ref)
                break

    def commit_refs(self):
        for de in self._defs:
            de.commit_refs()

    def get_defs(self):
        return self._defs

    def remove_short_defs(self, min_num_refs=Const.MIN_REFS_PER_DEF):
        for de in self._defs:
            if de.num_refs() < min_num_refs:
                del self._def_dic[de.tag]
        self.commit_defs()


class SourceBundle:

    def __init__(self):
        self._src_dic = dict()
        self._srcs = None

    def load(self, defs_file, refs_file, syms_file):
        self._read_defs_file(defs_file)
        self._read_refs_file(refs_file)
        self._read_syms_file(syms_file)

        for src in self._srcs:
            src.remove_short_defs()
            src.commit_refs()

    def _read_defs_file(self, defs_file):
        with open(defs_file, encoding=Const.SOURCE_ENCODING) as fl:
            for line in fl:
                tag, line_num, src_name, def_line = self._parse_line(line)
                if not src_name in self._src_dic:
                    self._src_dic[src_name] = SourceFile(src_name)
                self._src_dic[src_name].add_def(tag, line_num, def_line)

        self._srcs = sorted(self._src_dic.values(), key=lambda s: s.name)
        for src in self._srcs:
            src.commit_defs()
    
    def _read_refs_file(self, refs_file, unified_len=0, unified_word=None):
        with open(refs_file, encoding=Const.SOURCE_ENCODING) as fl:
            for line in fl:
                ref_tag, line_num, src_name, ref_line = self._parse_line(line)
                if not src_name in self._src_dic:
                    print('WARN: source ' + src_name + ' is not defined',
                          file=sys.stderr)
                    continue
                ref = Reference(ref_tag, line_num, ref_line)
                if len(ref_tag) <= unified_len:
                    ref.word = unified_word
                self._src_dic[src_name].add_ref(ref)
        
    def _read_syms_file(self, syms_file):
        self._read_refs_file(
            syms_file, Const.UNIFIED_SYM_LENGTH, Const.UNIFIED_SYM_WORD)
        
    def _parse_line(self, line):
        tag, line_num, src_name, content = re.split(r'\s+', line.strip(), 3)
        return tag, int(line_num), src_name, content

    def save_labels(self, out_file):
        with open(out_file, 'w') as fl:
            for src in self._srcs:
                for de in src.get_defs():
                    fields = [src.name, de.tag,
                              str(de.line_num), str(de.tail_line_num())]
                    fl.write(Const.LABEL_FIELD_DELIMITER.join(fields) + '\n')

    def save_docs(self, out_file):
        with open(out_file, 'w') as fl:
            for src in self._srcs:
                for de in src.get_defs():
                    words = [r.word for r in de.get_refs()]
                    fl.write(Const.DOC_WORD_DELIMITER.join(words) + '\n')

    def save_debug(self, out_file):
        with open(out_file, 'w') as fl:
            for src in self._srcs:
                fl.write('#src %s\n' % src.name)
                for de in src.get_defs():
                    fl.write('    %4d %s: %s\n' % (
                        de.line_num, de.tag, de.def_line))
                    for ref in de.get_refs():
                        addition = ' -> ' +ref.word if ref.is_unified() else ''
                        fl.write('        %4d %s%s\n' % (
                            ref.line_num, ref.tag, addition))


def resolve_input_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--defs-file', '-d', default=None,
                        help='input definition tags file')
    parser.add_argument('--refs-file', '-r', default=None,
                        help='input reference tags file')
    parser.add_argument('--syms-file', '-s', default=None,
                        help='input symbol tags file')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    defs_file = resolve_input_path(conf, conf.defs_file, Const.TAGS_DEF_FNAME)
    refs_file = resolve_input_path(conf, conf.refs_file, Const.TAGS_REF_FNAME)
    syms_file = resolve_input_path(conf, conf.syms_file, Const.TAGS_SYM_FNAME)

    bundle = SourceBundle()
    bundle.load(defs_file, refs_file, syms_file)

    if not os.path.exists(conf.out_dir):
        os.mkdir(conf.out_dir)
    bundle.save_labels(os.path.join(conf.out_dir, Const.LABELS_FNAME))
    bundle.save_docs(os.path.join(conf.out_dir, Const.DOCS_FNAME))
    bundle.save_debug(os.path.join(conf.out_dir, Const.DEBUG_FUNCS_FNAME))
