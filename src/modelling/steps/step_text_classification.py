from datetime import datetime
import pandas as pd 
import numpy as np
from tqdm import tqdm
import evaluate
import torch
from datasets import Dataset, DatasetDict
from omegaconf import DictConfig

from peft import LoraConfig, TaskType, get_peft_model, PeftModel
from transformers import (TrainingArguments,
                            Trainer,
                            AutoTokenizer,
                            AutoModelForSequenceClassification)

from src.utils.utils_crawler import (save_json,
                                     read_json)
from src.utils.utils_models import print_trainable_parameters
from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing
from src.constants.class_map import class_mapping


class StepTextClassification(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig, 
                 save_model : bool = True):

        super().__init__(context=context, config=config)

        self.ratio_validation = self._config.text_classification.ratio_validation
        self.model_name = self._config.text_classification.model
        self.train_batch_size = self._config.text_classification.train_batch_size
        self.test_batch_size = self._config.text_classification.test_batch_size
        self.device = self._config.text_classification.device
        self.epochs = self._config.text_classification.epochs
        self.finetuned_model_name = self._config.text_classification.fine_tuned_model

        self.save_model = save_model
        self.today = datetime.today().strftime("%d_%m_%Y")

    def create_training_data(self):

        df = self.read_sql_data("SELECT * FROM \"PICTURES_CATEGORY_20_04_2024\" WHERE \"PROBA_0\" > 0.95")
        df = df[[self.name.id_item, self.name.total_description, "TOP_0"]]
        df = df.loc[df[self.name.total_description].apply(lambda x: len(x))> 100]
        df["TOP_0"] = df["TOP_0"].map(class_mapping)
        volume_classes = df["TOP_0"].value_counts().loc[df["TOP_0"].value_counts() > 15].index
        df = df.loc[df["TOP_0"].isin(volume_classes)]

        # sample per class
        total_sample_size = 400
        id_items_to_keep = df.groupby('TOP_0').apply(lambda x: x[self.name.id_item][:total_sample_size]).values
        df = df.loc[df[self.name.id_item].isin(id_items_to_keep)]
        # df.to_csv("D:/data/test_classif.csv", index=False, sep=";")

        df.rename(columns={"TOP_0": "labels", "TOTAL_DESCRIPTION": "text"}, inplace=True)

        return df 
    
    def split_train_test(self, df):

        df_validation = df.sample(frac= self.ratio_validation)
        df_train = df.drop(df_validation.index)
                
        train = Dataset.from_pandas(df_train)
        validation = Dataset.from_pandas(df_validation)

        dataset = DatasetDict()
        dataset['train'] = train
        dataset['validation'] = validation

        return dataset

    @timing
    def training(self):

        df = self.create_training_data()
        print(df.head())
        self.classes_2id = self.define_num_classes(df["labels"].unique())
        df["labels"] = df["labels"].map(self.classes_2id)
        dataset = self.split_train_test(df)

        self.load_tokenizer()
        tokenized_datasets = dataset.map(self.tokenize_text, batched=True)

        self.lora_config = self.set_lora_config()
        self.base_model = self.load_base_model(model_name=self.model_name)
        self.text_model = get_peft_model(self.base_model, self.lora_config)
        print_trainable_parameters(self.text_model)

        self.metric = evaluate.load("accuracy")
        self.trainer  = self.get_trainer(tokenized_datasets["train"],
                                         tokenized_datasets["validation"])
        self.trainer.train()
        
        if self.save_model:
            self.trainer.save_model(self.finetuned_model_name)
            self.tokenizer.save_model(self.finetuned_model_name)
            save_json(self.classes_2id,
                      path=self.finetuned_model_name + "/classes_2id.json")

        return self.text_model

    def predicting(self):

        df = self.create_training_data()
        self.classes_2id = self.load_classes_id()
        self.id_2classes = self.reverse_classes_id(self.classes_2id)
        dataset = self.split_train_test(df)

        self.batching = torch.utils.data.DataLoader(dataset["validation"], 
                                                    shuffle=False, 
                                                    batch_size=self.test_batch_size)

        #load model & tokenizer
        self.load_tokenizer()
        self.fine_tuned_model = self.load_peft_finetuned_model(model_name=self.model_name)

        # predict labels 
        answers = self.batched_prediction(self.fine_tuned_model, self.batching)

        # reshape top_k answers
        df_answers = self.clean_answers(answers)
        df_answers["text"] = dataset["validation"]["text"]
        df_answers["labels"] = dataset["validation"]["labels"]

        return df_answers

    def batched_prediction(self, model, batching):
        answers = []
        for batch in tqdm(batching):
            tokenized_inputs = self.tokenize_text(batch).to(self.device)
            model_prediction = self.model_prediction(model, tokenized_inputs, self.top_k)
            answers.append(model_prediction)
        return answers

    def model_prediction(self, model, batch_dict, top_k=5):
        with torch.no_grad():
            outputs = model(**batch_dict)
            lsm = torch.nn.functional.softmax(outputs.logits, dim=-1)
            answers = torch.topk(lsm, k=top_k)
        return answers

    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def tokenize_text(self, df):
        return self.tokenizer(df["text"], 
                              padding="max_length", 
                              max_length=512,
                              truncation=True, 
                              return_tensors='pt')

    def set_lora_config(self):
        return LoraConfig(
            task_type=TaskType.SEQ_CLS,
            r=32,
            lora_alpha=1,
            lora_dropout=0.1
        )

    def load_base_model(self, model_name):
        return AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=len(self.classes_2id.keys()),
            device_map="auto"
        )
    
    def load_peft_finetuned_model(self, model_name):
      base_model = self.load_base_model(model_name)
      finetuned_model = PeftModel.from_pretrained(base_model, 
                                                  self.finetuned_model_name, 
                                                  is_trainable=False)
      return finetuned_model.eval()

    def define_num_classes(self, classes):

        self.classes_2id = {}
        for i, classe in enumerate(classes):
            self.classes_2id[classe] = i

        return self.classes_2id
    
    def load_classes_id(self):
        return read_json(self.finetuned_model_name + "/classes_2id.json")
    
    def reverse_classes_id(self, classes_2id):
        return {v: k for k,v in classes_2id.items()}

    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return self.metric.compute(predictions=predictions, references=labels)

    def get_trainer(self, train_data, test_data):
        training_args = TrainingArguments(output_dir="test_trainer",
                                          evaluation_strategy="steps",
                                          num_train_epochs=self.epochs,
                                          per_device_train_batch_size=self.train_batch_size,
                                          lr_scheduler_type="linear",
                                          report_to="tensorboard",
                                          warmup_ratio=0.03,
                                          save_steps=1500,
                                          group_by_length=True,
                                          logging_steps=1500,
                                          learning_rate=2e-4)
        return Trainer(
                model=self.text_model,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=test_data,
                compute_metrics=self.compute_metrics
            )
        
    def clean_answers(self, answers):
        proba_cols = [f"PROBA_{i}" for i in range(self.top_k)]
        classes_cols = [f"TOP_{i}" for i in range(self.top_k)]
        columns = proba_cols + classes_cols

        total = pd.DataFrame()
        for batch in answers:
            probas, classes = batch[0].cpu().numpy(), batch[1].cpu().numpy()
            batch_total = pd.concat([pd.DataFrame(probas), pd.DataFrame(classes)], axis=1)
            total = pd.concat([total, batch_total], axis=0)

        for col in classes_cols:
          total[col] = total[col].map(self.id_2classes)

        total.columns = columns
        return total.reset_index(drop=True)
