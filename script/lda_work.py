# -*- coding: utf-8 -*-

import os
import re
import argparse

import gensim
from gensim.models import LdaModel
from gensim.models import TfidfModel
from gensim.corpora.dictionary import Dictionary

import pyLDAvis.gensim
import pandas


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


def convert_corpus_by_tfidf(tfidf, corpus):
    '''for LDAViz convert freq to int'''
    def modify_bow(bow):
        return [(pair[0], int(pair[1] * 1000)) for pair in bow]

    return [modify_bow(tfidf[bow]) for bow in corpus]


class LdaWorker:

    def __init__(self):
        self._lda = None
        self._dictionary = None
        self.num_topics = None
        self._corpus = None
 
    def load_docs(self, docs_file):
        docs = read_docs_as_matrix(docs_file)
        self._dictionary = Dictionary(docs)

        # Transforming corpus with dictionary.
        self._corpus = [self._dictionary.doc2bow(doc) for doc in docs]

        tfidf = gensim.models.TfidfModel(self._corpus)
        #self._corpus = tfidf[self._corpus]
        self._corpus = convert_corpus_by_tfidf(tfidf, self._corpus)
 
    def init_model(self, num_topics):
        self._lda = LdaModel(corpus=self._corpus,
                             id2word=self._dictionary,
                             num_topics=num_topics)

    def save_model(self, out_file):
        self._lda.save(out_file)
     
    def save_html(self, out_file):
        lda = self._lda
        data = pyLDAvis.gensim.prepare(lda, self._corpus, self._dictionary)
        pyLDAvis.save_html(data, out_file)

    def save_info(self, out_dir):
        model = self._lda
        
        # 文書ごとトピック分布をCSV出力
        topic_dist_per_doc = [dict(model[bow]) for bow in self._corpus]
        pandas.DataFrame(topic_dist_per_doc).to_csv(
            os.path.join(out_dir, "topic_dist_per_doc.csv"))

        # トピックごとの単語分布（上位10語）をCSV出力
        # Sequence with (topic_id, [(word, value), … ]).
        # list of (int, list of (str, float))
        topicdata = model.print_topics(num_topics=-1, num_words=10)
        pandas.DataFrame(topicdata).to_csv(
            os.path.join(out_dir, "topic_detail.csv"))

        print('num_topics=%d' % model.num_topics)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--labels-file', '-l', default=None,
                        help="input labels file")
    parser.add_argument('--num-topics', '-n', type=int,
                        default=20, help='number of topics')
    parser.add_argument('--out-dir', '-o', required=True,
                        help='output dir')
    
    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    if not os.path.exists(conf.out_dir):
        os.mkdir(conf.out_dir)

    worker = LdaWorker()
    worker.load_docs(conf.docs_file)
    
    worker.init_model(conf.num_topics)
    
    worker.save_model(os.path.join(conf.out_dir, 'lda_model'))
    worker.save_info(conf.out_dir)
    worker.save_html(os.path.join(conf.out_dir, 'dist.html'))
