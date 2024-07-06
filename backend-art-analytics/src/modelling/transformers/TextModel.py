from tqdm import tqdm
from torch.utils.data import DataLoader, Dataset
from sentence_transformers import SentenceTransformer
import gc
import time
import torch
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
        model_name: str,
        prompt: str = None,
        text_type: str = "text_en",
    ):

        super().__init__(context=context, config=config)

        self.prompt = prompt
        self.text_type = text_type
        self.model_name = model_name
        self.batch_size = self._config.embedding.text.batch_size
        self.prompt_name = self._config.embedding.prompt_name
        device = self._config.embedding.device
        self.max_length = 4096

        if not self.model_name:
            raise Exception("Either model name or model path should be given")

        # model params
        if not device:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

    def load_model(self):

        self.text_model = SentenceTransformer(
            self.model_name,
            trust_remote_code=True,
            device=self.device,
            prompts=self.prompt,
        )
        self.text_model = self.text_model.half()
        torch.cuda.empty_cache()
        gc.collect()

    def embed_texts(self, texts):
        dataset = TextDataset(texts, max_length=self.max_length)
        dataloader = DataLoader(
            dataset, batch_size=self.batch_size * 1000, shuffle=False
        )

        embeddings = []

        for batch in tqdm(dataloader):
            batch = list(batch)
            with torch.no_grad():
                batch_embeddings = self.text_model.encode(
                    batch,
                    convert_to_tensor=True,
                    device=self.device,
                    batch_size=self.batch_size,
                    prompt_name=self.prompt_name,
                )
                # self.text_model(**batch)
                embeddings.append(batch_embeddings.cpu())

                for _ in range(50):
                    torch.cuda.empty_cache()
                    gc.collect()
                    time.sleep(0.1)

        return torch.cat(embeddings)
