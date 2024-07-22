import os
from huggingface_hub import HfApi
import subprocess

os.environ["TORCH_SHOW_CPP_STACKTRACES"] = "1"

from datasets import load_dataset
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, AutoPeftModelForCausalLM
from trl import SFTTrainer

from src.utils.utils_models import print_trainable_parameters
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from huggingface_hub import login

from omegaconf import DictConfig

PROMPT = """You are an art expert. Extract a valid JSON object from the art description. Only return valid json and nothing else. Write all JSON values only in english, translate them if necessary.
JSON Schema: {"object_category": str, "object_sub_category": str, "object_subject": str, "object_brand": str, "object_material": str, "object_length": str, "object_width": str, "object_height": str, "object_weight": str, "object_signed": str, "object_condition": str, "number_objects_described" : str, "object_period_or_year": str}
Object category is the family of object the description is about. For instance a Bowl, a Vase, a Chair, a Table, etc.
Object sub category refers to a more specific part of the family of object. For instance a ceramic bowl, a glass vase, a watercolor painting etc. Give only the concept of the sub family with few words only.
Object subject refers to what the picture is about, or what is displayed on a picture, etc.
Number of objects described refers to the number of items described in the text below. Render only a number.
Dimensions such as length, height, width are in centimeter and weight in grams."""


def prompt_llama3(prompt, input, output):
    return f"""<|start_header_id|>system<|end_header_id|> {prompt} <|eot_id|><|start_header_id|>user<|end_header_id|> {input} <|eot_id|><|start_header_id|>assistant<|end_header_id|> {output} <|eot_id|>"""


def prompt_llam3_generate(prompt, input):
    return f"""<|start_header_id|>system<|end_header_id|> {prompt} <|eot_id|><|start_header_id|>user<|end_header_id|> {input} <|eot_id|>"""


def prompt_mixtral_7b(prompt, input, output):
    return (
        f"""<s>[INST] {prompt} here are the inputs {input} [/INST] \\n {output} </s>"""
    )


def formatting_prompts_func(PROMPT, examples):
    output_texts = []
    for i in range(len(examples["ID_ITEM"])):
        output_texts.append(
            prompt_llama3(PROMPT, examples["input"][i], examples["output"][i])
        )
    return output_texts


class TrainTextModel(Step):

    def __init__(self, context: Context, config: DictConfig, device: str = None):

        super().__init__(context=context, config=config)

        self.origin_model_name = self._config.llm.origin_model_name
        self.model_new_name = self._config.llm.new_model_name
        self.model_path = self._config.llm.model_path
        self.temp_folder = self._config.llm.temp_folder
        self.personal_repo = self._config.llm.hug_repo

        self.epochs = self._config.llm.params.epochs
        self.batch_size = self._config.llm.params.batch_size

        login(token=os.environ["HUGGINGFACE_TOKEN"])
        self.hughface_api = HfApi()

        if not self.model_name and not self.model_path:
            raise Exception("Either model name or model path should be given")

        # model params
        if not device:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

    def fit(self, inputs):

        train_data = load_dataset(
            "json", data_files=self.train_data_path, split="train"
        )
        test_data = load_dataset("json", data_files=self.test_data_path, split="train")

        self.load_model(model_name=self.origin_model_name)
        self.load_tokenize(model_name=self.origin_model_name)
        self.declare_peft_params()
        self.declare_training_params(save_path=self.temp_folder)

        self.model = get_peft_model(self.model, self.peft_params)
        print_trainable_parameters(self.model)

        self.trainer = SFTTrainer(
            model=self.model,
            train_dataset=train_data,
            eval_dataset=test_data,
            formatting_func=formatting_prompts_func,
            peft_config=self.peft_params,
            max_seq_length=2048,
            tokenizer=self.tokenizer,
            args=self.training_params,
            packing=False,
        )

        self.trainer.train()
        self.save_model(self.model_new_name)

    def load_model(self, model_name):

        compute_dtype = getattr(torch, "float16")

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=False,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quant_config,
            torch_dtype=torch.bfloat16,
            device_map={"": 0},
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )
        self.model.config.use_cache = False
        self.model.config.pretraining_tp = 1
        self.model.gradient_checkpointing_enable()

    def load_tokenize(self, model_name):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

    def declare_peft_params(self):
        self.peft_params = LoraConfig(
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
                "lm_head",
            ],
            r=64,
            bias="none",
            task_type="CAUSAL_LM",
        )

    def declare_training_params(self, save_path):
        self.training_params = TrainingArguments(
            output_dir=save_path,
            num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=1,
            optim="paged_adamw_32bit",
            save_steps=50,
            logging_steps=50,
            learning_rate=2e-4,
            weight_decay=0.001,
            fp16=True,
            bf16=False,
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_ratio=0.03,
            group_by_length=True,
            lr_scheduler_type="cosine",
            report_to="tensorboard",
            evaluation_strategy="no",  # steps or epochs if true
        )

    def save_model(self, new_model_path):
        self.trainer.model.save_pretrained(new_model_path)
        self.trainer.tokenizer.save_pretrained(new_model_path)

    def run_from_qlora_saved(self):

        self.check_model_in_huggingface(f"{self.personal_repo}/{self.model_new_name}")
        self.merge_model(
            origin_model_name=self.origin_model_name,
            new_model_name=f"{self.personal_repo}/{self.model_new_name}",
        )
        result = self.run_llama_cpp_quantization()

        if result == 1:
            self.upload_file_to_hughface()

    def check_model_in_huggingface(self, model_name):
        try:
            model_info = self.hughface_api.model_info(model_name)
        except Exception:
            self._log.error(
                f"NEW MODEL ON HUGGINGFACE does not exist, check adldl/{model_name}"
            )

    def merge_model(self, origin_model_name, new_model_name):

        model_path_name = "/".join([self.model_path, self.model_new_name])
        model = AutoPeftModelForCausalLM.from_pretrained(
            new_model_name,
            torch_dtype=torch.float16,
            return_dict=False,
            device_map="cpu",
        )

        tokenizer = AutoTokenizer.from_pretrained(origin_model_name)

        merged_model = model.merge_and_unload()
        merged_model.save_pretrained(model_path_name + "-merged")
        tokenizer.save_pretrained(model_path_name + "-merged")

    def run_llama_cpp_quantization(self):
        # then llama.cpp/convert.py "model" --outfile meta_llama3_finetuned.fp16.bin --outtype f16 --vocab-type bpe
        # then llama.cpp/quantize "D:/data/models/meta_llama3_finetuned.f16.bin" "D:/data/models/meta_llama3_finetuned-q4_k_m.gguf" q4_K_M

        model_path_name = "/".join([self.model_path, self.model_new_name + "-merged"])
        cmd = subprocess.Popen(
            [
                "python",
                "C:/Users/alarr/Documents/repos/llama.cpp/convert.py",
                model_path_name,
                "--outfile",
                f"{model_path_name}/{self.model_new_name}.fp16.bin",
                "--outtype",
                "f16",
                "--vocab-type",
                "bpe",
            ]
        )
        cmd.communicate()

        cmd = subprocess.Popen(
            [
                "C:/Users/alarr/Documents/repos/llama.cpp/build/bin/Release/quantize",
                f"{model_path_name}/{self.model_new_name}.fp16.bin",
                f"{model_path_name}/{self.model_new_name}-q4_k_m.gguf",
                "q4_K_M",
            ]
        )
        cmd.communicate()

        return 1

    def upload_file_to_hughface(self):
        model_path_name = "/".join([self.model_path, self.model_new_name])

        self.hughface_api.upload_file(
            path_or_fileobj=f"{model_path_name}-merged/{self.model_new_name}-q4_k_m.gguf",
            path_in_repo=f"{self.model_new_name}-q4_k_m.gguf",
            repo_id=f"{self.personal_repo}/{self.model_new_name}",
            repo_type="model",
        )
