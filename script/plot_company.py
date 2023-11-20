import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from arin_apify.reddit_dao_mongo import RedditDaoMongo
from matplotlib import pyplot as plt
from pandas import DataFrame
from tqdm import tqdm
from wordcloud import STOPWORDS, WordCloud

from arin_reddittools.tools_reddit import compute_sha256, unwrap_content


def create_wordcloud_rel(group_name: str, dict_content: Dict[str, str]) -> None:
    pass
    # https://towardsdatascience.com/generate-meaningful-word-clouds-in-python-5b85f5668eeb
    # TODO we can make this year specific
    # https://github.com/bryan-md/wordcloud/blob/main/wordcloud.ipynb


def create_wordcloud(
    group_name: str, title: str, list_content_instance: List[str], list_exclude: List[str] = []
) -> None:
    if not os.path.isdir(group_name):
        os.mkdir(group_name)
    print(f"create_wordlcoud {title}", flush=True)
    path_file = os.path.join(group_name, f"wordcloud_{title}.png")
    if os.path.exists(path_file):
        return
    comment_words = ""
    stopwords = set(STOPWORDS)
    for exclude in list_exclude:
        stopwords.add(exclude)
    stopwords.add("s")
    stopwords.add("u")
    stopwords.add("gt")

    stopwords.add("one")
    stopwords.add("time")
    stopwords.add("year")
    stopwords.add("years")
    stopwords.add("month")
    stopwords.add("months")
    stopwords.add("week")
    stopwords.add("weeks")
    stopwords.add("day")
    stopwords.add("days")
    stopwords.add("lt")
    stopwords.add("people")

    stopwords.add("http")
    stopwords.add("https")
    stopwords.add("com")
    stopwords.add("www")
    stopwords.add("ect")
    stopwords.add("gov")
    stopwords.add("html")

    stopwords.add("really")
    stopwords.add("lot")
    stopwords.add("much")
    stopwords.add("many")
    stopwords.add("still")
    stopwords.add("well")
    stopwords.add("right")

    stopwords.add("take")
    stopwords.add("will")
    stopwords.add("go")
    stopwords.add("going")
    stopwords.add("make")
    stopwords.add("want")
    stopwords.add("think")
    stopwords.add("know")

    # iterate through the csv file
    for content_instance in tqdm(list_content_instance):
        # split the value
        list_token = content_instance.lower().split()
        comment_words += " ".join(list_token) + " "

    wordcloud = WordCloud(
        width=800,
        height=800,
        background_color="white",
        stopwords=stopwords,
        min_font_size=10,
    ).generate(comment_words)

    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    # save

    plt.savefig(path_file)
    # plt.show()


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_all"

    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    connection_string: str = os.getenv("ARIN_APIFY_MONGO_CONNECTIONSTRING")  # type: ignore
    database_name = "arin-apify"
    dao_mongo = RedditDaoMongo(connection_string, database_name, batch_size=10)
    scrape_config = await dao_mongo.scrape_config.load(scrape_id)
    scrape_state = await dao_mongo.scrape_state.load(scrape_id)

    with open(path_file_dict_instance_selected, "r") as file:
        dict_instance = json.load(file)

    list_company = []
    list_company.append("moderna")
    list_company.append("pfizer")
    list_company.append("johnson")
    list_company.append("janssen")
    list_company.append("astrazeneca")
    list_company.append("novavax")
    list_company.append("covaxin")
    dict_bin = {}
    for company in list_company:
        dict_bin[company] = []
    for list_post in dict_instance.values():
        for post in list_post:
            for company in list_company:
                if company in post["content"].lower():
                    dict_bin[company].append(post["content"])

    # create_wordlcoud(dict_year_bin["2023"])
    # create_wordlcoud(dict_year_bin["2022"])
    for company in list_company:
        create_wordcloud("company", company, dict_bin[company], list_exclude=list_company)


#    created_at


if __name__ == "__main__":
    asyncio.run(main())
