# -*- coding: utf-8 -*-

import os
import re
import argparse

import gensim
from gensim.models import LdaModel
from gensim.models import TfidfModel
from gensim.corpora.dictionary import Dictionary
import pyLDAvis.gensim
import pandas as pd

from analysis_const import Const


def read_docs_as_matrix(docs_file):
    docs = []
    with open(docs_file) as fl:
        for line in fl:
            words = re.split(r'\s+', line.strip())
            docs.append(words)
    return docs


def read_src_names(labels_file):
    lines = []
    with open(labels_file) as fl:
        for line in fl:
            lines.append(line.split('\t')[0].strip())
    return lines


def resolve_io_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def ldaviz_convert_corpus_by_tfidf(tfidf: TfidfModel, corpus: list) -> list:
    '''for LDAViz convert freq to int'''
    def modify_bow(bow):
        return [(pair[0], int(pair[1] * 1000)) for pair in bow]

    return [modify_bow(tfidf[bow]) for bow in corpus]


class LdaWorker:

    def __init__(self, with_ldavis=False):
        self._lda = None
        self._dictionary = None
        self.num_topics = None
        self._corpus = None
        self._labels = None
        self._with_ldavis = with_ldavis
 
    def load_docs(self, docs_file, labels_file):
        docs = read_docs_as_matrix(docs_file)
        self._labels = read_src_names(labels_file)

        self._dictionary = Dictionary(docs)

        # Transforming corpus with dictionary.
        self._corpus = [self._dictionary.doc2bow(doc) for doc in docs]

        tfidf = gensim.models.TfidfModel(self._corpus)

        if self._with_ldavis:
            self._corpus = ldaviz_convert_corpus_by_tfidf(tfidf, self._corpus)
        else:
            self._corpus = tfidf[self._corpus]
 
    def init_model(self, num_topics: int) -> None:
        self._lda = LdaModel(corpus=self._corpus,
                             id2word=self._dictionary,
                             num_topics=num_topics)

    def save_model(self, out_file):
        self._lda.save(out_file)
     
    def save_html_by_ldavis(self, out_file):
        data = pyLDAvis.gensim.prepare(self._lda, self._corpus, self._dictionary)
        pyLDAvis.save_html(data, out_file)

    def save_info(self, out_dir):
        model = self._lda
        
        # 文書ごとのトピック分布をCSV出力
        topics_per_doc = [
            # list of (int, float) – Topic distribution for the whole document.
            # Each element in the list is a pair of a topic’s id,
            # and the probability that was assigned to it.
            dict(model.get_document_topics(bow)) for bow in self._corpus]
        df = pd.DataFrame(topics_per_doc, index=self._labels)
        df.to_csv(os.path.join(out_dir, "topics_per_doc.csv"))
        df.fillna(0).to_csv(os.path.join(out_dir, "doc_topic_matrix.csv"),
            header=False, index=False)

        # トピックごとの単語分布（上位30語）をCSV出力
        df = pd.DataFrame()
        for topic_id in range(model.num_topics):
            # [(WordID, probability)...]
            topic_terms = model.get_topic_terms(topic_id, topn=30)
            col_term = '%d_word' % topic_id
            col_prob = '%d_prob' % topic_id
            df[col_term] = [model.id2word[wid] for wid, _ in topic_terms]
            df[col_prob] = [prob for _, prob in topic_terms]
        df.to_csv(os.path.join(out_dir, "topic_words.csv"), index=False)

        # Sequence with (topic_id, [(word, value), … ]).
        # list of (int, list of (str, float))
        #topicdata = model.print_topics(num_topics=-1, num_words=30)
        #pd.DataFrame(topicdata).to_csv(
        #    os.path.join(out_dir, "topic_detail.csv"))

        print('num_topics=%d' % model.num_topics)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--docs-file', '-d', default=None,
                        help='input documents file')
    parser.add_argument('--labels-file', '-l', default=None,
                        help="input labels file")
    parser.add_argument('--num-topics', '-n', type=int,
                        default=10, help='number of topics')
    parser.add_argument('--out-dir', '-o', required=True,
                        help='output dir')
    parser.add_argument('--with-ldavis', action='store_true',
                        default=False, help='output LDAVis html')
    
    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    docs_file = resolve_io_path(conf, conf.docs_file, Const.DOCS_FNAME)
    labels_file = resolve_io_path(conf, conf.labels_file, Const.LABELS_FNAME)

    if not os.path.exists(conf.out_dir):
        os.mkdir(conf.out_dir)

    worker = LdaWorker(with_ldavis=conf.with_ldavis)
    worker.load_docs(docs_file, labels_file)
    
    worker.init_model(conf.num_topics)
    
    worker.save_model(os.path.join(conf.out_dir, 'lda_model'))
    worker.save_info(conf.out_dir)

    if conf.with_ldavis:
        worker.save_html_by_ldavis(os.path.join(conf.out_dir, "ldavis.html"))
