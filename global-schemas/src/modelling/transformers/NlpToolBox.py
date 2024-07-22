from typing import List
import pandas as pd
import re
import numpy as np
import swifter
from nltk import ngrams

from src.utils.timing import timing
from src.utils.utils_dataframe import remove_accents
from sklearn.feature_extraction.text import CountVectorizer

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

import nltk

nltk.download("stopwords")

from nltk.corpus import stopwords


class NLPToolBox:

    def __init__(self):

        self.stopwords = stopwords.words("french") + stopwords.words("english")
        self.words_vect = None
        self.port_stemmer = PorterStemmer()

    @timing
    def simple_homegenize(self, vect):

        # lowerise
        vect = vect.str.lower()

        # remove accents
        vect = vect.swifter.apply(lambda x: self.replace_nnp(x))

        return vect

    @timing
    def c_tf_idf(self, documents: List[str], count_vectorizer: CountVectorizer):

        # calculate tf_idf
        number_docs = len(documents)
        t = count_vectorizer.transform(documents).toarray()
        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(number_docs, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        return tf_idf

    @timing
    def extract_top_n_words(self, text_list: List[str], ngram_range: tuple):
        """
        Extract top n words per text list
        """

        count_vectorizer = CountVectorizer(
            ngram_range=ngram_range,
            max_df=0.25,
            min_df=5,
            stop_words="english",
            max_features=1000,
        ).fit(text_list)

        words = count_vectorizer.get_feature_names_out()
        words = np.array(words)

        return count_vectorizer, words

    def extract_words_per_cluster(
        self, documents: List[str], ngram_range: tuple = (1, 2), n_top_words: int = 5
    ):

        # clean_text
        documents = self.simple_homegenize(documents)

        # top thousands words
        count_vectorizer, columns = self.extract_top_n_words(documents, ngram_range)

        # tf idf
        tf_idf = self.c_tf_idf(documents, count_vectorizer)
        tf_idf = tf_idf.T

        # shape result
        mapping_dict = {}
        for i, word in enumerate(columns):
            mapping_dict[i] = word

        tf_idf_index = np.argsort(tf_idf, axis=1)
        tf_idf_index = tf_idf_index[:, -n_top_words:]
        tf_idf_index = np.vectorize(mapping_dict.get)(tf_idf_index)

        answer_words = {}
        for i, id_cluster in enumerate(documents.index):
            answer_words[id_cluster] = list(tf_idf_index[i])

        return answer_words

    @timing
    def manuak_clustering(self, vect, manuals):

        if not isinstance(self.words_vect, pd.Series):
            self.split_into_ngrams(vect)

        cluster_words, weights, id_mapping = self.get_manual_clusters_infos(manuals)
        cluster = self.deduce_cluster(cluster_words, weights, id_mapping)

        return cluster

    @timing
    def split_into_ngrams(self, vect):
        self.words_vect = vect.swifter.apply(
            lambda x: [a for a in word_tokenize(x) if a not in self.stopwords]
        )
        self.words_vect = self.words_vect.swifter.apply(
            lambda x: x + [" ".join(a) for a in list(ngrams(x, 2))]
        )
        return self.words_vect

    @timing
    def deduce_cluster(self, cluster_words, weights, id_mapping):

        self.X = self.words_vect.swifter.apply(
            lambda x: self.words_intersect(x, cluster_words)
        )
        self.X = np.multiply(np.array(self.X.tolist()), np.array(weights))
        max_value = np.max(self.X, axis=1)
        cluster_id = np.argmax(self.X, axis=1)

        cluster = pd.Series(cluster_id).map(id_mapping)
        cluster = np.where(max_value == 0, np.nan, cluster)

        return cluster

    def get_manual_clusters_infos(self, manuals):

        cluster_words = []
        weights = []
        id_mapping = {}
        for i, (k, v) in enumerate(manuals.items()):
            cluster_words.append(set(v))
            weights.append(1 / np.log(1 + len(v)))
            id_mapping[i] = k

        return cluster_words, weights, id_mapping

    def words_intersect(self, x, cluster_words):
        return [len(set(x).intersection(cluster)) for cluster in cluster_words]

    def replace_nnp(self, x):
        """Input comment as a string to be cleaned up:
        - lower case
        - contraction handled
        - punctuation replace as ' '
        - strip and check multi spaces
        """

        # remove parenthesised text
        x = re.sub(r"\([^)]*\)", " ", x)

        # handle specific cases
        x = re.sub("/n", " ", x)
        x = re.sub("\n", " ", x)
        x = re.sub("&", " and ", x)
        x = re.sub("@", " at ", x)
        x = re.sub(" etc ", " ", x)

        # remove numbers
        x = re.sub(r"[0-9]", "", x)

        # punctuation removed
        x = re.sub("[^\\w\\s_]", " ", x)

        # remove accents
        x = remove_accents(x)

        # remove extra spaces
        x = re.sub(" + ", " ", x)

        # strip sides
        x = x.strip()

        return x

    def stemming(self, vect):

        vect_words = vect.swifter.apply(lambda x: word_tokenize(x))
        vect = vect_words.swifter.apply(lambda x: self.stemSentence(x))

        return vect

    def stemSentence(self, list_words):
        stem_sentence = []
        for word in list_words:
            stem_sentence.append(self.port_stemmer.stem(word))
        return " ".join(stem_sentence)
