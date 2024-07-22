from tqdm import tqdm
from typing import List
import gc
import time
import torch
from torch.utils.data import DataLoader, Dataset
from sentence_transformers import SentenceTransformer

from src.context import Context
from src.utils.step import Step

from omegaconf import DictConfig


class TextDataset(Dataset):
    def __init__(self, texts, max_length=4096):
        self.texts = texts
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        elmt = self.texts[idx]
        return elmt[: min(len(elmt), self.max_length)]


class TextModel(Step):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        prompt: str = None,
    ):

        super().__init__(context=context, config=config)

        self.prompt = prompt
        self.batch_size = self._config.embedding.text.batch_size
        self.prompt_name = self._config.embedding.prompt_name
        device = self._config.embedding.device
        self.max_length = 4096

        # model params
        if not device:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

    def load_model(self, model_name: str):

        text_model = SentenceTransformer(
            model_name, trust_remote_code=True, device=self.device, prompts=self.prompt
        )
        text_model = text_model.half()
        torch.cuda.empty_cache()
        gc.collect()

        return text_model

    def embed_texts(self, model, prompt_name: str, texts: List[str]):
        dataset = TextDataset(texts, max_length=self.max_length)
        dataloader = DataLoader(
            dataset, batch_size=self.batch_size * 1000, shuffle=False
        )

        embeddings = []

        for batch in tqdm(dataloader):
            batch = list(batch)
            with torch.no_grad():
                batch_embeddings = model.encode(
                    batch,
                    convert_to_tensor=True,
                    device=self.device,
                    batch_size=self.batch_size,
                    prompt_name=prompt_name,
                )
                embeddings.append(batch_embeddings.cpu())

                for _ in range(5):
                    torch.cuda.empty_cache()
                    gc.collect()
                    time.sleep(0.1)

        return torch.cat(embeddings)

    def embed_one_text(self, model, prompt_name, text):
        embedding = (
            model.encode(
                text,
                convert_to_tensor=True,
                device=self.device,
                prompt_name=prompt_name,
            )
            .cpu()
            .numpy()
        )
        torch.cuda.empty_cache()
        gc.collect()

        return embedding
