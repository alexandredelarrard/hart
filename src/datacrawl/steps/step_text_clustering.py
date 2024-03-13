from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.datacrawl.transformers.Clustering import TopicClustering

from omegaconf import DictConfig


class StepTextEmbedding(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig):

        super().__init__(context=context, config=config)
        

    def run(self, embeddings):

        step_cluster = TopicClustering()