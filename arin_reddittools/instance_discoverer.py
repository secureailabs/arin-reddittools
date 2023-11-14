import json
import os
import pickle as pkl
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import sklearn.metrics as metrics
from numpy import vectorize
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from tqdm import tqdm


class InstanceDiscoverer:
    def __init__(
        self,
        dict_instance: Dict[str, Any],
        dict_label: Dict[str, bool],
        dict_skip: Dict[str, bool],
        list_subreddit_show: List[str],
    ) -> None:
        self.dict_instance = dict_instance
        self.dict_label = dict_label
        self.dict_skip = dict_skip
        self.list_subreddit_show = list_subreddit_show

    def print_instance(self, instance_id: str):
        list_item = self.dict_instance[instance_id]
        for item in list_item:
            if item["subreddit"] in self.list_subreddit_show:
                print(item["content"])

        print(list_item[0]["author"])

    def rebuild_model(self):
        print(self.dict_instance.keys())
        count_true = 0
        count_false = 0
        for label in self.dict_label.values():
            if label:
                count_true += 1
            else:
                count_false += 1

        if count_true == 0 or count_false == 0:
            print("not enough labels, reverting")
            list_score_sorted = []
            for instance_id in self.dict_instance.keys():
                list_score_sorted.append((instance_id, 0.5))
            return list_score_sorted

        list_instance_id = []
        list_text = []
        list_label = []
        for instance_id, label in self.dict_label.items():
            list_instance_id.append(instance_id)
            instance = self.dict_instance[instance_id]
            print(instance)
            # TODO: fix this
            list_text.append(instance["content"])
            list_label.append(self.dict_label[instance_id])

        path_file_model = "model.pkl"
        if os.path.exists(path_file_model):
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

        y_true_num = [1 if label == True else 0 for label in list_label]

        # plot roc curve
        fpr, tpr, threshold = metrics.roc_curve(
            y_true_num,
            y_pred_prob[:, 0],
        )

        roc_auc = metrics.auc(fpr, tpr)
        print("possible mis labels")
        dict_score = {}
        for instance_id, pred_prob in zip(list_instance_id, y_pred_prob):
            dict_score[instance_id] = pred_prob[0]

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

    def get_candidates(self, count: int = 5):
        list_instance_id = None

    def loop(self):
        list_score_sorted = self.rebuild_model()
        print("list_score_sorted")
        print(len(list_score_sorted))
        for instance_id, score in list_score_sorted:
            if instance_id in self.dict_label:
                continue
            if instance_id in self.dict_skip:
                continue
            self.print_instance(instance_id)
            print(score)
            print("(1) add to selection")
            print("(2) do not add to selection")
            print("(s) skip")
            print("(c) clear all skip")
            print("(r) rebuild model")
            print("(q) to quit")
            user_input = ""
            while user_input not in ["1", "2", "q"]:
                user_input = input()
                if user_input == "1":
                    self.dict_label[instance_id] = True
                    with open("dict_label.json", "w") as file:
                        json.dump(self.dict_label, file, indent=4)
                elif user_input == "2":
                    self.dict_label[instance_id] = True
                    with open("dict_label.json", "w") as file:
                        json.dump(self.dict_label, file, indent=4)
                elif user_input == "c":
                    self.dict_skip = {}
                    with open("dict_skip.json", "w") as file:
                        json.dump(self.dict_skip, file, indent=4)
                elif user_input == "s":
                    self.dict_skip[instance_id] = True
                    with open("dict_skip.json", "w") as file:
                        json.dump(self.dict_skip, file, indent=4)
                elif user_input == "q":
                    exit()
                else:
                    print("invalid input")
