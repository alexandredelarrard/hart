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