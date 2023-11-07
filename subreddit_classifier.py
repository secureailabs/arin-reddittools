import json
import os
import pickle as pkl
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import sklearn.metrics as metrics
from numpy import vectorize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from tqdm import tqdm


def build_classifier(
    list_text: List[str], list_label: List[str], list_subreddit_name: List[str], retrain: bool = False
):
    path_file_model = "model.pkl"
    if os.path.exists(path_file_model) and not retrain:
        with open(path_file_model, "rb") as file:
            pipeline = pkl.load(file)
    else:
        # pipeline = Pipeline(
        #     [("vectorizer", CountVectorizer()), ("classifier", LogisticRegression(solver="lbfgs", max_iter=1000))]
        # )
        print("retraining", flush=True)
        # vectorizer = TfidfVectorizer(max_features=20)
        vectorizer = TfidfVectorizer(max_features=400)
        classifier = MultinomialNB()
        pipeline = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])
        pipeline.fit(list_text, list_label)
        with open(path_file_model, "wb") as file:
            pkl.dump(pipeline, file)

    y_pred = pipeline.predict(list_text)
    y_pred_prob = pipeline.predict_proba(list_text)
    # print(vectorizer.get_feature_names_out())
    # print(classifier.feature_log_prob_)
    print(accuracy_score(list_label, y_pred))
    print(confusion_matrix(list_label, y_pred))
    print(classification_report(list_label, y_pred))

    y_true_num = [1 if label == "med" else 0 for label in list_label]

    # plot roc curve
    fpr, tpr, threshold = metrics.roc_curve(
        y_true_num,
        y_pred_prob[:, 0],
    )

    roc_auc = metrics.auc(fpr, tpr)
    print("possible mis labels")
    dict_score = {}
    for subreddit_name, label, pred_prob in zip(list_subreddit_name, list_label, y_pred_prob):
        if label != "med":
            dict_score[subreddit_name] = pred_prob[0]

    list_score_sorted = sorted(dict_score.items(), key=lambda x: x[1], reverse=True)

    plt.title("Receiver Operating Characteristic")
    plt.plot(fpr, tpr, "b", label="AUC = %0.2f" % roc_auc)
    plt.legend(loc="lower right")
    plt.plot([0, 1], [0, 1], "r--")
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel("True Positive Rate")
    plt.xlabel("False Positive Rate")
    # plt.show()

    return list_score_sorted


def build_dataset(dataframe: pd.DataFrame, list_subreddit_med: List[str]):
    list_subreddit_name = dataframe["subreddit"].unique().tolist()
    list_subreddit_text = []
    list_subreddit_label = []
    max_token_count = 10000
    for subreddit in tqdm(list_subreddit_name):
        list_text = dataframe[dataframe["subreddit"] == subreddit]["text"].tolist()
        text = " ".join(list_text)
        list_token = text.split(" ")
        if max_token_count < len(list_token):
            list_token = list_token[:max_token_count]
            text = " ".join(list_token)
        list_subreddit_text.append(text)

        if subreddit in list_subreddit_med:
            list_subreddit_label.append("med")
        else:
            list_subreddit_label.append("non-med")
    dataset = {}
    dataset["text"] = list_subreddit_text
    dataset["label"] = list_subreddit_label
    dataset["name"] = list_subreddit_name
    return dataset


def main():
    with open("config_scrape_reddit.json", "r") as file:
        config = json.load(file)
    list_subreddit_medical = config["list_subreddit_medical"]
    list_subreddit_medical.extend(config["list_subreddit_medical_add"])
    dataframe = pd.read_csv("reddit_post.csv", dtype={"text": str})
    dataframe["text"] = dataframe["text"].fillna("")

    rebuild_dataset = True
    rebuild_model = True
    # filter on subreddit
    dataframe["class_is_med"] = dataframe["subreddit"].isin(list_subreddit_medical)
    if not os.path.exists("dataset.json") or rebuild_dataset:
        print("start build dataset", flush=True)
        dataset = build_dataset(dataframe, list_subreddit_medical)
        print("done build dataset", flush=True)
        with open("dataset.json", "w") as file:
            json.dump(dataset, file)
        list_subreddit_text = dataset["text"]
        list_subreddit_label = dataset["label"]
        list_subreddit_name = dataset["name"]
    else:
        with open("dataset.json", "r") as file:
            dataset = json.load(file)
        print("done loading dataset", flush=True)
        list_subreddit_text = dataset["text"]
        list_subreddit_label = dataset["label"]
        list_subreddit_name = dataset["name"]

    list_score_sorted = build_classifier(list_subreddit_text, list_subreddit_label, list_subreddit_name, rebuild_model)
    list_subreddit_medical_add = config["list_subreddit_medical_add"]
    list_subreddit_non_medical_add = config["list_subreddit_non_medical_add"]
    for subreddit_name, score in list_score_sorted:
        if subreddit_name in list_subreddit_medical:
            continue
        if subreddit_name in list_subreddit_medical_add:
            continue
        if subreddit_name in list_subreddit_non_medical_add:
            continue
        print(f"{subreddit_name} {score}")
        print("(1) add to medical")
        print("(2) add to non-medical")
        print("(q) to quit")
        user_input = ""
        while user_input not in ["1", "2", "q"]:
            user_input = input()
            if user_input == "1":
                list_subreddit_medical_add.append(subreddit_name)
                with open("config_scrape_reddit.json", "w") as file:
                    config["list_subreddit_medical_add"] = list_subreddit_medical_add
                    json.dump(config, file, indent=4)
            elif user_input == "2":
                list_subreddit_non_medical_add.append(subreddit_name)
                with open("config_scrape_reddit.json", "w") as file:
                    config["list_subreddit_non_medical_add"] = list_subreddit_non_medical_add
                    json.dump(config, file, indent=4)
            elif user_input == "q":
                exit()
            else:
                print("invalid input")


# ShittyLifeProTips

if __name__ == "__main__":
    main()
