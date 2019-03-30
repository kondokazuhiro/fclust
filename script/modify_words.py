# -*- coding: utf-8 -*-

'''
modify words
'''

import os
import re
import argparse

from analysis_const import Const


def read_docs_as_matrix(docs_file: str) -> list:
    docs = []
    with open(docs_file) as fl:
        for line in fl:
            words = re.split(r'\s+', line.strip())
            docs.append(words)
    return docs


def split_word(word: str) -> list:
    # ex. __CamelCase__ -> __Camel_Case__
    snake = re.sub('([A-Z]+)', r'_\1', word)
    # ex. __Camel_Case__ -> Camel_Case__
    snake = re.sub('^_+', '', snake)
    # ex. Camel_Case__ -> Camel_Case
    snake = re.sub('_+$', '', snake)
    # ex. ['Camel', 'Case']
    return re.split('_+', snake)

def modify_words(in_words: list) -> list:
    out_words = []
    for word in in_words:
        words = split_word(word)
        out_words.extend(words)
    return out_words


def modify_docs_with_save(out_file, docs):
    with open(out_file, 'w') as fl:
        for words in docs:
            fl.write(' '.join(modify_words(words)))
            fl.write('\n')
               

def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--out-docs-file', default=None,
                        help='output documents file')
    parser.add_argument('--out-dir', '-o', default=None,
                        help='output dir')
    parser.add_argument('--min-length', type=int, default=2,
                        help='minimum word length')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    in_docs_file = resolve_io_path(conf, conf.docs_file, Const.DOCS_FNAME)
    out_docs_file = resolve_io_path(conf, conf.out_docs_file, Const.DOCS_FNAME)
    docs = read_docs_as_matrix(in_docs_file)
    modify_docs_with_save(out_docs_file, docs)
