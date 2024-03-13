from sklearn import cluster

import re
from src.utils.timing import timing

import hdbscan
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from sklearn.neighbors import NearestNeighbors
import scipy.cluster.hierarchy as sch
import scipy.spatial.distance as ssd
from sklearn.cluster import AgglomerativeClustering
import pandas as pd 
from typing import List
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
import logging

import seaborn as sns
sns.set_theme(style="darkgrid")


class TopicClustering(object):

    def __init__(self, params={}):
        """Use weights from 

        Args:
            params (dict, optional): [description]. Defaults to {}.
        """

        self.params = params 
        

    @timing
    def hdbscan_clustering(self, embeddings : np.array) -> List[int]:
        """
        HDBSCAN clustering on text embedded

        Args:
            embeddings (np.array): [embedding of text from bert pre trained model]

        Returns:
            List[int]: [labels of cluster]
        """

        logging.info("#"*50)
        logging.info("|| HDBSCAN CLUSTERING ||")
        logging.info("#"*50)

        dbscan = hdbscan.HDBSCAN(min_cluster_size=self.params["min_cluster_size"],
                                min_samples= self.params["min_samples"],
                                metric='minkowski',  
                                # cluster_selection_epsilon= self.params["cluster_selection_epsilon"],
                                p=2,                    
                                cluster_selection_method='leaf',
                                algorithm='best', 
                                alpha=1.0, 
                                core_dist_n_jobs = multiprocessing.cpu_count() -1)
        cluster = dbscan.fit(embeddings)

        return cluster.labels_


    def CAH_clustering(self, embeddings, threshold) -> List[int]:
        """
        Hierarchical clustering based on embeddings of each cluster previously identified. 
        It get current clusters, aggregate their text as one large paragraph and create embeddings 
        from bert pre trained model. 
        Then CAH performed grouping together sub clusters below threshold_cah parameter.

        Args:
            df (pd.DataFrame): [dataframe with text to cluster and previously clustered output]
            corpus_text_cluster (pd.DataFrame): [dataframe with one row per cluster and concatenated 
                                                comments in one paragraph]

        Returns:
            List[int]: [New higher level cluster output]
        """

        model = AgglomerativeClustering(distance_threshold=None, 
                                        n_clusters=threshold,
                                        affinity="cosine",
                                        linkage = "average")
        model = model.fit(embeddings)
        cah_clusters = model.labels_

        return cah_clusters
    

    def plot_clusters(self, df):

        # Visualize clusters
        fig, ax = plt.subplots(figsize=(15, 15))
        outliers = df.loc[df.labels == -1]
        clustered = df.loc[df.labels != -1]
        plt.scatter(outliers.x, outliers.y, color='#696464', s=0.2)
        plt.scatter(clustered.x, clustered.y, c=clustered.labels, s=0.2, cmap='hsv_r')
        plt.colorbar()
        plt.show()


    def c_tf_idf(self, documents : List[str], m : int, ngram_range : tuple):

        count = CountVectorizer(ngram_range=ngram_range, max_df=0.5, min_df=2).fit(documents)

        t = count.transform(documents).toarray()
        w = t.sum(axis=1)
        tf = np.divide(t.T, w)
        sum_t = t.sum(axis=0)
        idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
        tf_idf = np.multiply(tf, idf)

        return tf_idf, count


    def extract_tf_idf_words(self, cluster_name : str):
        """
        Extract top n words for each cluster ID made by cluster_name trategy

        Args:
            docs_per_topic ([type]): [dataframe with all comments per row and clustered output so far]
            cluster_name ([type]): [cluster strategy as str]

        Returns:
            [pd.DataFrame, Dict]: [top words as paragraph in dataframe, dictionnary of top n words per cluster ID]
        """

        docs_per_topic = self.data[["CLEAN_TEXT", cluster_name]].groupby([cluster_name], as_index = False).agg({"CLEAN_TEXT": ' '.join})
        
        tf_idf, count = self.c_tf_idf(docs_per_topic["CLEAN_TEXT"].values, 
                                        m=docs_per_topic.shape[0], 
                                        ngram_range=self.params["ngram_range"])
        
        words = count.get_feature_names()
        labels = list(docs_per_topic[cluster_name])
        tf_idf_transposed = tf_idf.T
        indices = tf_idf_transposed.argsort()[:, -self.params["n_words_cluster"]:]
        top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
        
        docs_per_topic["TOP_WORDS"] = docs_per_topic[cluster_name].apply(lambda x: list(zip(*top_n_words[x][:self.params["n_words_cluster"]]))[0])

        return docs_per_topic, top_n_words


    def extract_top_n_words(self):
        """
        Extract top n words for each cluster ID made by cluster_name trategy

        Args:
            cluster_name ([type]): [cluster strategy as str]

        Returns:
            [pd.DataFrame, Dict]: [top words as paragraph in dataframe, dictionnary of top n words per cluster ID]
        """

        # get top words for all text
        text = self.data["CLEAN_TEXT"].tolist()

        # stemming text
        # text = text.apply(lambda x : self.stemSentence(x))
        count = CountVectorizer(ngram_range=self.params["ngram_range"], 
                                max_df=0.5,
                                min_df=2).fit(text)
        
        words = count.get_feature_names()
        words = np.array(words)

        return words 
        
        
    def get_closest_words_to_centroid(self, words, cluster_centroid_embeddings, cluster_name):

        # calculate closest words neighbors of cluster centroids 
        neigh = NearestNeighbors(n_neighbors=self.params["n_words_cluster"])
        neigh.fit(self.top_words_embeddings)
        mapping_words = neigh.kneighbors(cluster_centroid_embeddings)

        top_n_words = {-1 : [("",0)]*self.params["n_words_cluster"]}
        labels = list(set(self.data[cluster_name].unique()) - set([-1]))

        centroides_words = []
        for i, cluster_id in enumerate(np.sort(labels)):
            top_n_words[cluster_id] = [(words[mapping_words[1][i][k]], mapping_words[0][i][k]) for k in range(len(mapping_words[1][i]))]
            centroides_words.append(np.mean(self.top_words_embeddings[mapping_words[1][i][:5]], axis=0))
        
        return top_n_words, np.array(centroides_words)

    
    def cluster_centroid_deduction(self, cluster_method): 

        clustered_data = self.data.loc[self.data[cluster_method]!=-1]
        centroids = []

        for cluster_id in np.sort(clustered_data[cluster_method].unique()):
            sub_data = clustered_data.loc[clustered_data[cluster_method] == cluster_id, "INDEX"].tolist()
            sub_embeddings = self.bert_embeddings[sub_data]
            centroids.append(np.mean(sub_embeddings, axis=0))

        return np.array(centroids)


    def treebuild_cah_clustering(self, centroids_words_cluster):

        logging.info("#"*50)
        logging.info("|| CAH CLUSTERING ||")
        logging.info("#"*50)

        k=1
        clusters_cah_tree= pd.DataFrame()
        nbr_clusters= len(self.data["HDBSCAN_CLUSTER"].unique()) - 1 # because of -1 cluster

        while 2**k < nbr_clusters:
            clusters_cah_tree[f"CAH_CLUSTER_{2**k}"], model = self.CAH_clustering(centroids_words_cluster, 2**k)
            k+=1

        if self.params["verbose"] > 1:
            model = AgglomerativeClustering(distance_threshold=0, 
                                        n_clusters=None,
                                        affinity="cosine",
                                        linkage = "average")
            model = model.fit(centroids_words_cluster)
            plt.figure(figsize=(10,10))
            plt.title('Hierarchical Clustering Dendrogram')
            # plot the top three levels of the dendrogram
            # plot_dendrogram(model, truncate_mode='level', p=16)
            plt.xlabel("Number of points in node (or index of point if no parenthesis).")
            plt.show()

        if self.params["verbose"] > 1:
                self.visualize_cluster(self.embeddings_reduction, clusters_cah_tree[f"CAH_CLUSTER_{2**(k-1)}"])  

        return clusters_cah_tree


    def closest_text_to_centroid(self, cluster_centroid_embeddings, cluster_name, top_k_text=2):

        df_cluster = self.data[["INDEX", cluster_name, "TARGET"]]
        df_cluster.index = df_cluster["INDEX"]

        neigh = NearestNeighbors(n_neighbors=top_k_text)
        neigh.fit(self.bert_embeddings)
        mapping_words = neigh.kneighbors(cluster_centroid_embeddings)

        mapped_text = pd.DataFrame(index=range(len(df_cluster[cluster_name].unique()) - 1))
        for id_text in range(top_k_text):
            mapped_text[f"CLOSEST_TEXT_{id_text}"] = list(zip(*mapping_words[1]))[id_text]
            mapped_text[f"CLOSEST_TEXT_{id_text}"] = mapped_text[f"CLOSEST_TEXT_{id_text}"].map(df_cluster["TARGET"])
            
        return mapped_text.to_dict(orient="records")


    def cluster_corr(self, corr_array : np.array, inplace=False) -> np.array:
        """
        Rearranges the correlation matrix, corr_array, so that groups of highly 
        correlated variables are next to eachother 

        Parameters
        ----------
        corr_array : pandas.DataFrame or numpy.ndarray
            a NxN correlation matrix 
            
        Returns
        -------
        pandas.DataFrame or numpy.ndarray
            a NxN correlation matrix with the columns and rows rearranged
        """

        pairwise_distances = sch.distance.pdist(corr_array)
        linkage = sch.linkage(pairwise_distances, method='complete')
        cluster_distance_threshold = pairwise_distances.max()/2
        idx_to_cluster_array = sch.fcluster(linkage, cluster_distance_threshold, 
                                            criterion='distance')
        idx = np.argsort(idx_to_cluster_array)

        if not inplace:
            corr_array = corr_array.copy()

        if isinstance(corr_array, pd.DataFrame):
            return corr_array.iloc[idx, :].T.iloc[idx, :]

        return corr_array[idx, :][:, idx]
