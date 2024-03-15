from llama_cpp import Llama

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
    model_path="./data/mixtral-8x7B-hf/mixtral-8x7b-v0.1.Q4_K_M.gguf",  # Download the model file first
    n_ctx=1024,  # The max sequence length to use - note that longer sequence lengths require much more resources
    n_threads=0,            # The number of CPU threads to use, tailor to your system and the resulting performance
    n_gpu_layers=35
)

from llama_cpp import Llama
llm = Llama(model_path="./data/mixtral-8x7B-hf/mixtral-8x7b-v0.1.Q4_K_M.gguf", n_gpu_layers=30, n_ctx=3584, n_batch=521, verbose=True)
# adjust n_gpu_layers as per your GPU and model
output = llm(f"Q: Quel matériau à l'objet dont la description est la suivante : {desc} A: ", max_tokens=512, stop=["Q:", "\n"], echo=True)
print(output["choices"][0]["text"].split("A:")[1])


from transformers import AutoModelForCausalLM, AutoTokenizer
device = "cuda"
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

from transformers import pipeline

text_generation_pipeline = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
    temperature=0.2,
    repetition_penalty=1.2,
    max_new_tokens=500,
    device=0, # -1 CPU, 0 GPU
    top_k=50,
    top_p=0.95,
    do_sample=True,
    pad_token_id = 50256,
    max_new_tokens = 128
)

from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
mistral_llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

desc = "SHAKER en métal argenté. H.24.5 cm. Usures d'usage. On joint une passoire à cocktail et un petit chauffe-plat"
prompt = f"Identifie le metal de l'objet décrit ci-après : {desc}"

a = mistral_llm.invoke(prompt)
print(a)

# ne fonctionne pas 
from transformers import pipeline   
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer, ViTModel

model = ViTModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")


image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
image_to_text(image_path)
pixel_values = feature_extractor(images=[i_image], return_tensors="pt").pixel_values


from transformers import AutoImageProcessor, AutoModel
from transformers import Swinv2Config, Swinv2Model

configuration = Swinv2Config()
model = Swinv2Model(configuration)
configuration = model.config
model.device = "cuda"

from transformers import AutoFeatureExtractor, AutoModel
from transformers import AutoImageProcessor, Swinv2Model

model_ckpt = "microsoft/swinv2-tiny-patch4-window8-256"
processor = AutoImageProcessor.from_pretrained(model_ckpt)
extractor = AutoFeatureExtractor.from_pretrained(model_ckpt)
model = Swinv2Model.from_pretrained(model_ckpt)


import torch 
import torchvision.transforms as T

# Data transformation chain.
transformation_chain = T.Compose(
    [
        # We first resize the input image to 256x256 and then we take center crop.
        T.Resize(int((256 / 224) * extractor.size["height"])),
        T.CenterCrop(extractor.size["height"]),
        T.ToTensor(),
        T.Normalize(mean=extractor.image_mean, std=extractor.image_std),
    ]
)

def extract_embeddings(model: torch.nn.Module, images):
    """Utility to compute embeddings."""
    device = model.device

    def pp(images):
        # `transformation_chain` is a compostion of preprocessing
        # transformations we apply to the input images to prepare them
        # for the model. For more details, check out the accompanying Colab Notebook.
        image_batch_transformed = torch.stack(
            [transformation_chain(image) for image in images]
        )
        new_batch = {"pixel_values": image_batch_transformed.to(device)}
        with torch.no_grad():
            embeddings = model(**new_batch).last_hidden_state[:, 0]
        return embeddings

    return pp(images)

import glob
import numpy as np
import pandas as pd 

list_pictures = glob.glob(r"C:\Users\alarr\Documents\repos\hart\data\drouot\pictures\*.jpg.jpg")
subset = list_pictures[100:120]

candidate_subset = []
for image in subset:
    candidate_subset.append(Image.open(image))

# image_path = r"C:\Users\alarr\Documents\repos\hart\data\drouot\pictures\1_2941_199.jpg.jpg"
# i_image = Image.open(image_path)
batch_size=4
device = "cuda" if torch.cuda.is_available() else "cpu"
extract_fn = extract_embeddings(model.to(device))

steps = len(candidate_subset) // batch_size 
for i in range(steps):
    images= candidate_subset[i*batch_size:(i+1)*batch_size]
    extract = extract_embeddings(model, images).numpy()
    if i == 0:
        candidate_subset_emb = extract
    else:
        candidate_subset_emb = np.concatenate((candidate_subset_emb, extract))
    