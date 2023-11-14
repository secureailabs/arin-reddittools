import json
from typing import Dict, List

import pandas as pd
from matplotlib import pyplot as plt


def show_bar_plot(dict_count):
    plt.figure()

    plt.bar(range(len(dict_count)), list(dict_count.values()), align="center")
    plt.title("Mention Count of words on Reddit")
    plt.ylabel("Mention Count")
    plt.xticks(range(len(dict_count)), list(dict_count.keys()))


# filter on supreddit
def count_keyword(list_text: List[str], list_keyword: List[str]) -> Dict[str, int]:
    list_text_lower = [text.lower() for text in list_text]
    list_keyword_lower = [keyword.lower() for keyword in list_keyword]
    dict_count = {}
    for keyword in list_keyword_lower:
        dict_count[keyword] = 0

    for text in list_text_lower:
        for keyword in list_keyword_lower:
            if keyword in text:
                dict_count[keyword] += 1
    return dict_count


def main():
    with open("config_scrape_reddit.json", "r") as file:
        config = json.load(file)
    list_subreddit = config["list_subreddit"]
    dataframe = pd.read_csv("list_item.csv", dtype={"text": str})
    dataframe["text"] = dataframe["text"].fillna("")

    # filter on subreddit
    print(len(dataframe))
    dataframe = dataframe[dataframe["subreddit"].isin(list_subreddit)]
    print(len(dataframe))
    list_text: List[str] = dataframe["text"].tolist()

    list_medication = [
        "apixaban",
        "arixtra",
        "coumadin",
        "dabigatran",
        "dalteparin",
        "edoxaban",
        "eliquis",
        "enoxaparin",
        "fondaparinux",
        "fragmin",
        "heparin",
        "lovenox",
        "pradaxa",
        "rivaroxaban",
        "savaysa",
        "warfarin",
        "xarelto",
    ]
    dict_count = count_keyword(list_text, list_medication)
    print(dict_count)
    show_bar_plot(dict_count)

    list_concept = [
        "chemo",
        "ICU",
        "HIPAA",
        "IC",
        "inpatient",
        "outpatient",
        "medication",
        "meds",
        "med",
        "drug",
        "drugs",
        "prescription",
        "prescriptions",
        "Rx",
        "Rx's",
        "Rx's",
        "treatment",
        "treatments",
        "therapy",
        "therapies",
        "therapeutic",
        "therapeutics",
        "therapeutically",
    ]
    dict_count = count_keyword(list_text, list_concept)
    print(dict_count)
    show_bar_plot(dict_count)

    list_vendor = [
        "Pfizer",
        "Johnson",
        "Merck",
        "Eli Lilly",
        "Bristol-Myers",
        "Amgen",
        "Gilead",
    ]
    dict_count = count_keyword(list_text, list_vendor)
    print(dict_count)
    show_bar_plot(dict_count)

    plt.show()


if __name__ == "__main__":
    main()
