import json
from typing import Dict, List

import pandas as pd
from matplotlib import pyplot as plt
from transformers import pipeline


def show_pieplot(title: str, dict_prediction_count: Dict[str, int]):
    plt.figure()
    labels = list(dict_prediction_count.keys())
    sizes = list(dict_prediction_count.values())
    plt.title(title)
    plt.pie(sizes, labels=labels)
    plt.legend(labels, loc="best")


# filter on supreddit
def count_sentiment_int(list_text: List[str], keyword: str) -> Dict[str, int]:
    classifier = pipeline(
        "text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", return_all_scores=True
    )

    list_text_lower = [text.lower() for text in list_text]
    keyword_lower = keyword.lower()
    dict_prediction_count = {}

    max_char_count = 1500
    # TODO we should rely on the tokenizer for this
    for text in list_text_lower:
        if keyword_lower in text:
            if max_char_count < len(text):
                text = text[:max_char_count]
            list_prediction = classifier(text)[0]  # type: ignore

            # sort by score
            prediction = sorted(list_prediction, key=lambda x: x["score"], reverse=True)[0]

            label = prediction["label"]
            print(label)
            if label not in dict_prediction_count:
                dict_prediction_count[label] = 0
            dict_prediction_count[label] += 1
    return dict_prediction_count


def main():
    with open("config_scrape_reddit.json", "r") as file:
        config = json.load(file)
    list_subreddit = config["list_subreddit"]
    dataframe = pd.read_csv("reddit_post.csv", dtype={"text": str})
    dataframe["text"] = dataframe["text"].fillna("")

    # filter on subreddit
    print(len(dataframe))
    dataframe = dataframe[dataframe["subreddit"].isin(list_subreddit)]
    print(len(dataframe))
    list_text: List[str] = dataframe["text"].tolist()
    list_vendor = [
        "Pfizer",
        "Johnson",
        "Merck",
        "Eli Lilly",
        "Bristol-Myers",
        "Amgen",
        "Gilead",
    ]
    for vendor in list_vendor:
        dict_prediction_count = count_sentiment_int(list_text, vendor)
        if 0 < len(dict_prediction_count):
            show_pieplot(vendor, dict_prediction_count)
            plt.savefig(f"sentiment_{vendor}.png")
        else:
            print(f"no sentiment for {vendor}")
    plt.show()


if __name__ == "__main__":
    main()
