import logging
import os 
os.environ["TORCH_SHOW_CPP_STACKTRACES"]="1"

from datasets import load_dataset
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline
)
from peft import LoraConfig, get_peft_model 
from trl import SFTTrainer  

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from omegaconf import DictConfig

PROMPT="""You are an art expert. Extract a valid JSON object from the art description. Only return valid json and nothing else. Write all JSON values only in english, translate them if necessary. 
JSON Schema: {"object_category": str, "object_sub_category": str, "object_brand": str, "number_objects_described" : str, "object_period_or_year": str}
Object category is the family of object the description is about. For instance a Bowl, a Vase, a Chair, etc. 
Object sub category refers to a more specific part of the family of object. For instance a ceramic bowl, a glass vase, a night dress etc. Give only the concept of the sub family with few words only.
Number of objects described refers to the number of items described in the text below. Render only a number."""

def prompt_llama3(prompt, input, output):
    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>{prompt}<|eot_id|>
            <|start_header_id|>user<|end_header_id|>{input}<|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>{output}<|eot_id|><|end_of_text|>"""

def prompt_mixtral_7b(prompt, input, output):
    return f"""<s>[INST] {prompt} here are the inputs {input} [/INST] \\n {output} </s>"""

def formatting_prompts_func(examples):
    output_texts = []
    for i in range(len(examples['ID_ITEM'])):
        output_texts.append(prompt_mixtral_7b(PROMPT, 
                                            examples["input"][i], 
                                            examples["output"][i]))
    return output_texts

def print_trainable_parameters(model):
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    logging.info(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    ) 

class TextModel(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 model_name : str,
                 model_path : str = None,
                 batch_size : int = 1,
                 device : str = None,
                 epochs : int = 1):

        super().__init__(context=context, config=config)

        self.model_name = model_name
        self.epochs = epochs
        self.batch_size=batch_size
        self.model_path = model_path

        if not self.model_name and not self.model_path:
            raise Exception("Either model name or model path should be given")

        # get classes
        self.batching = {}

        # model params
        if not device:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

    def fit(self, inputs):
        
        train_data = load_dataset('json', data_files='D:/data/llm_log/train_test_vase.jsonl', split='train')

        self.load_model()
        self.load_tokenize()
        self.declare_peft_params()
        self.declare_training_params(save_path="D:/data/models")

        self.model = get_peft_model(self.model, self.peft_params)
        print_trainable_parameters(self.model)

        self.trainer = SFTTrainer(
            model=self.model,
            train_dataset=train_data,
            # eval_dataset=test_data,
            formatting_func=formatting_prompts_func,
            peft_config=self.peft_params,
            # dataset_text_field="text",
            max_seq_length=512,
            tokenizer=self.tokenizer,
            args=self.training_params,
            packing=False
        )

        self.trainer.train()


    def load_model(self):

        compute_dtype = getattr(torch, "float16")

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=False,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        quantization_config=quant_config,
                        device_map="balanced",
                        max_memory={0: "6GiB", "cpu": "20GiB"}
                    )
        self.model.config.use_cache = False
        self.model.config.pretraining_tp = 1

    def load_tokenize(self):
        from huggingface_hub import login
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

    def declare_peft_params(self):
        self.peft_params = LoraConfig(
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj","lm_head"],
                r=64,
                bias="none",
                task_type="CAUSAL_LM",
            )
    
    def declare_training_params(self, save_path):
        self.training_params = TrainingArguments(
                output_dir=save_path,
                num_train_epochs=self.epochs,
                per_device_train_batch_size=1,
                gradient_accumulation_steps=1,
                optim="paged_adamw_32bit",
                save_steps=25,
                logging_steps=25,
                learning_rate=2e-4,
                weight_decay=0.001,
                fp16=True,
                bf16=False,
                max_grad_norm=0.3,
                max_steps=-1,
                warmup_ratio=0.03,
                group_by_length=True,
                lr_scheduler_type="constant",
                report_to="tensorboard"
            )
    
    def save_model(self, new_model_path):
        self.trainer.model.save_pretrained(new_model_path)
        self.trainer.tokenizer.save_pretrained(new_model_path)
    