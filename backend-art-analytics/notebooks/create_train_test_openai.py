import json
import pandas as pd

DEFAULT_SYSTEM_PROMPT = """You are an art expert. You extract caracteristics from art descriptions in JSON format. Your answers are in english. You only render found information.
                        Format of the JSON output is:
                        [{"object_category": str,
                        "vase_shape": str,
                        "vase_style_or_manufacturer": str,
                        "vase_material": str,
                        "vase_color": str,
                        "number_described_objects": str,
                        "vase_periode_or_circa_year": str,
                        "vase_height": str,
                        "vase_decoractions": str,
                        "vase_signed": str,
                        "vase_condition": str,
                        "vase_country": str}]"""


def create_dataset(description, features):
    return {
        "messages": [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": "Art Description: " + description},
            {"role": "assistant", "content": features},
        ]
    }


def write_jsonl(df):
    with open("D:/data/train.jsonl", "w") as f:
        for _, row in df.iterrows():
            example_str = json.dumps(create_dataset(row["Question"], row["Answer"]))
            f.write(example_str + "\n")


if __name__ == "__main__":
    df = pd.read_csv("path/to/file.csv", encoding="cp1252")
