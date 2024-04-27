from datetime import datetime
import pandas as pd 
import numpy as np
import evaluate
from datasets import Dataset, DatasetDict
from omegaconf import DictConfig

from peft import LoraConfig, TaskType, get_peft_model
from transformers import (TrainingArguments,
                            Trainer,
                            AutoTokenizer,
                            AutoModelForSequenceClassification)

from src.utils.utils_crawler import save_json
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
        self.fine_tuned_model = self._config.text_classification.fine_tuned_model

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
        total_sample_size = 350
        id_items_to_keep = df.groupby('TOP_0').apply(lambda x: x[self.name.id_item][:total_sample_size]).values
        df = df.loc[df[self.name.id_item].isin(id_items_to_keep)]
        df.to_csv("D:/data/test_classif.csv", index=False, sep=";")

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
        self.classes_2id = self.define_num_classes(df["TOP_0"].unique())
        dataset = self.split_train_test(df)

        self.load_tokenizer()
        tokenized_datasets = dataset.map(self.tokenize_text, batched=True)
        small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
        small_eval_dataset = tokenized_datasets["validation"].shuffle(seed=42).select(range(1000))

        self.lora_config = self.set_lora_config()
        self.base_model = self.load_base_model()
        self.text_model = get_peft_model(self.base_model, self.lora_config)
        print_trainable_parameters(self.text_model)

        self.metric = evaluate.load("accuracy")
        self.trainer  = self.get_trainer(small_train_dataset, small_eval_dataset)
        self.trainer.train()
        
        if self.save_model:
            self.text_model.save_model(self.fine_tuned_model)
            save_json(self.classes_2id, 
                      path=self.fine_tuned_model + "/classes_2id.json")
        
        return self.text_model

    @timing
    def predicting(self):
        return 0
    
    @timing
    def load_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def tokenize_text(self, df):
        return self.tokenizer(df[self.name.total_description], padding="max_length", truncation=True)

    @timing
    def set_lora_config(self):
        return LoraConfig(
            task_type=TaskType.SEQ_CLS, 
            r=16, 
            lora_alpha=1, 
            lora_dropout=0.1
        )

    @timing
    def load_base_model(self):
        return AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=len(self.classes_2id.keys())
        )

    @timing
    def define_num_classes(self, classes):

        self.classes_2id = {}
        for i, classe in enumerate(classes):
            self.classes_2id[classe] = i

        return self.classes_2id
    
    @timing
    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return self.metric.compute(predictions=predictions, references=labels)
    
    @timing
    def get_trainer(self, train_data, test_data):
        training_args = TrainingArguments(output_dir=self.fine_tuned_model, 
                                        evaluation_strategy="steps",
                                        num_train_epochs=self.epochs,
                                        per_device_train_batch_size=self.train_batch_size,
                                        lr_scheduler_type="constant",
                                        report_to="tensorboard",
                                        warmup_ratio=0.03,
                                        group_by_length=True,
                                        logging_steps=500,
                                        learning_rate=2e-4)
        
        return Trainer(
                model=self.text_model,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=test_data,
                compute_metrics=self.compute_metrics
            )
