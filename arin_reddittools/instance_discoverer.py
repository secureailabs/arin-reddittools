import json
import os
import pickle as pkl
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import sklearn.metrics as metrics
from arin_apify.reddit_dao_mongo import RedditDaoMongo
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
        dao_mongo: RedditDaoMongo,
        scrape_id: str,
        discovery_id: str,
        dict_instance: Dict[str, Any],
        list_subreddit_show: List[str],
    ) -> None:
        self.dao_mongo = dao_mongo
        self.scrape_id = scrape_id
        self.discovery_id = discovery_id
        self.dict_instance = dict_instance
        self.discovery_state = {}
        self.list_subreddit_show = list_subreddit_show

    def print_instance(self, instance_id: str):
        list_item = self.dict_instance[instance_id]
        dict_count = {}
        for item in list_item:
            if item["subreddit"] not in dict_count:
                dict_count[item["subreddit"]] = 0
            dict_count[item["subreddit"]] += 1
        for subreddit, count in dict_count.items():
            print(f"{subreddit}: {count}")

        for item in list_item:
            if item["subreddit"] in self.list_subreddit_show:
                print(item["content"])

        print(list_item[0]["author"])

    def rebuild_model(self):
        print(self.dict_instance.keys())
        count_true = 0
        count_false = 0
        for label in self.discovery_state["dict_label"].values():
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
        print(self.discovery_state["dict_label"])
        for instance_id, label in self.discovery_state["dict_label"].items():
            if instance_id not in self.dict_instance:
                continue
            list_instance_id.append(instance_id)
            instance = self.dict_instance[instance_id]
            list_string = [item["content"] for item in instance]
            list_text.append(" ".join(list_string))
            list_label.append(self.discovery_state["dict_label"][instance_id])

            # path_file_model = "model.pkl"
            # if os.path.exists(path_file_model):
            #     with open(path_file_model, "rb") as file:
            #         pipeline = pkl.load(file)
            # else:
        print("retraining", flush=True)
        vectorizer = CountVectorizer()
        classifier = LogisticRegression(solver="lbfgs", max_iter=3)
        # pipeline = Pipeline(
        #     [("vectorizer", CountVectorizer()), ("classifier", LogisticRegression(solver="lbfgs", max_iter=1000))]
        # )

        # vectorizer = TfidfVectorizer(max_features=20)
        # vectorizer = TfidfVectorizer(max_features=400)
        # classifier = MultinomialNB()
        pipeline = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])
        pipeline.fit(list_text, list_label)
        path_file_model = "model.pkl"
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

        plt.title("Receiver Operating Characteristic")
        plt.plot(fpr, tpr, "b", label="AUC = %0.2f" % roc_auc)
        plt.legend(loc="lower right")
        plt.plot([0, 1], [0, 1], "r--")
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.ylabel("True Positive Rate")
        plt.xlabel("False Positive Rate")
        # plt.show()

        # Predict for all instances to sort the list
        list_instance_id_all = []
        list_text_all = []
        for instance_id, instance in self.dict_instance.items():
            list_instance_id_all.append(instance_id)
            list_text_all.append(" ".join([item["content"] for item in instance]))

        dict_score = {}
        y_pred_prob_all = pipeline.predict_proba(list_text_all)[:, 0]
        for instance_id, pred_prob in zip(list_instance_id_all, y_pred_prob_all):
            dict_score[instance_id] = pred_prob
        list_score_sorted = sorted(dict_score.items(), key=lambda x: x[1], reverse=False)
        return list_score_sorted

    def get_candidates(self, count: int = 5):
        list_instance_id = None

    async def loop(self):
        if await self.dao_mongo.discovery_state.has(self.discovery_id):
            self.discovery_state = await self.dao_mongo.discovery_state.load(self.discovery_id)
        else:
            self.discovery_state = {}
            self.discovery_state["dict_label"] = {}
            self.discovery_state["dict_skip"] = {}

            scrape_config = await self.dao_mongo.scrape_config.load(self.scrape_id)
            list_username_source = scrape_config["list_username_source"]
            for username in list_username_source:
                self.discovery_state["dict_label"][username] = True
            await self.dao_mongo.discovery_state.save(self.discovery_id, self.discovery_state)

        list_score_sorted = self.rebuild_model()
        print("list_score_sorted")
        print(len(list_score_sorted))
        for instance_id, score in list_score_sorted:
            if instance_id in self.discovery_state["dict_label"]:
                continue
            if instance_id in self.discovery_state["dict_skip"]:
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
            while user_input not in ["1", "2", "s", "c", "r", "q"]:
                user_input = input()
                if user_input == "1":
                    self.discovery_state["dict_label"] = True
                    await self.dao_mongo.discovery_state.save(self.discovery_id, self.discovery_state)
                elif user_input == "2":
                    self.discovery_state["dict_label"] = False
                    await self.dao_mongo.discovery_state.save(self.discovery_id, self.discovery_state)
                elif user_input == "c":
                    self.discovery_state["dict_skip"] = {}
                    await self.dao_mongo.discovery_state.save(self.discovery_id, self.discovery_state)
                elif user_input == "s":
                    self.discovery_state["dict_skip"] = True
                    await self.dao_mongo.discovery_state.save(self.discovery_id, self.discovery_state)
                elif user_input == "q":
                    exit()
                else:
                    print("invalid input")
