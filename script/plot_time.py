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


def create_wordcloud(group_name: str, year_str: str, list_content_instance: List[str]) -> None:
    if not os.path.isdir(group_name):
        os.mkdir(group_name)
    print(f"create_wordlcoud {year_str}", flush=True)
    path_file = os.path.join(group_name, f"wordcloud_{year_str}.png")
    if os.path.exists(path_file):
        return
    comment_words = ""
    stopwords = set(STOPWORDS)
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

    list_timestamp = []
    dict_year_bin = {}
    for list_post in dict_instance.values():
        for post in list_post:
            # if "sick" in post["content"].lower():
            list_timestamp.append(post["created_at"])
            year_str = str(datetime.fromtimestamp(post["created_at"]).year)
            if year_str not in dict_year_bin:
                dict_year_bin[year_str] = []
            dict_year_bin[year_str].append(post["content"])

    # timestamp to data
    print(datetime.fromtimestamp(list_timestamp[0]))
    list_timestamp.sort()
    print(datetime.fromtimestamp(list_timestamp[-1]))
    plt.hist(list_timestamp)
    plt.show()
    print(dict_year_bin.keys())

    # create_wordlcoud(dict_year_bin["2023"])
    # create_wordlcoud(dict_year_bin["2022"])
    for year_str in sorted(list(dict_year_bin.keys())):
        create_wordcloud("base", year_str, dict_year_bin[year_str])


#    created_at


if __name__ == "__main__":
    asyncio.run(main())
