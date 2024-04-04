import openai
import os 
import random
from tqdm import tqdm
import pandas as pd 
from src.context import get_config_context
from src.modelling.steps.step_manual_cluster import StepManualCluster

api_key = "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"
os.environ["OPENAI_API_KEY"] = api_key

def creat_messages(list_text):
    messages = []

    for text in list_text:
        messages.append({"role": "user", 
                         "content": """prompt : Extract information of the art description with the following schema, null if not provided, 
                                    schema : {
                                            "text infered object category": str,
                                            "artiste": str,
                                            "object length": str,
                                            "object height": str,
                                            "object depth": str,
                                            "object weight": float,
                                            "period or year": str,
                                            "number pieces": int,
                                            "object material": str,
                                            "is signed": bool,
                                            "certificate": str,    
                                            "object condition": str,
                                            "object motif details": str
                                        }
                                    text : "%s"""%text})
    return messages

# watch test 
schema : {
        "category": "watch",
        "house": str,
        "gender" : str,
        "watch name" : str,
        "period or year": str,
        "bracelet material": str,
        "case material": str,
        "case shape": str,
        "number complications" : int,
        "type of movement":  str,
        "object condition": str,
        "box available": str,
        "certificate available" : bool,
        "watch diametre" : float,
    }

def retreiver(client, messages):
    answers = []
    for message in tqdm(messages):
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            seed=1234,
            messages=[message],
            stream=False,       
        )

        answers.append(stream.choices[0].message.content.replace("null", "\"Null\"").replace("false", "False").replace("true", "True"))

    return answers


def clean_answeres(answers):

    final = []
    for answer in answers:
        final.append(eval(answer.replace("\"\"", "\"")))

    return pd.DataFrame(final)


if __name__ == "__main__":
    # depend de la catégorie 
    # text retreiver après que catégorie déduite
    
    client = openai.OpenAI()

    config, context = get_config_context('./configs', use_cache = False, save=False)
    step =  StepManualCluster(context=context, config=config, database_name="all")

    df = step.get_data()
    list_text = random.sample(df[step.name.total_description].tolist(), 100)

    messages = creat_messages(list_text)
    answers = retreiver(client, messages)

    df = clean_answeres(answers)