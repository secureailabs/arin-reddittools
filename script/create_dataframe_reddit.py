import json
from typing import Dict, List

from arin_apify.reddit_dao_disk import RedditDaoDisk


def collect_dict_item(item: dict) -> Dict[str, dict]:
    dict_item = {}
    frame_item = {}
    frame_item["id"] = item["id"]
    frame_item["author"] = item["author"]
    frame_item["url"] = item["url"]
    frame_item["subreddit"] = item["subreddit"]
    frame_item["score"] = item["score"]
    if "text" in item:
        frame_item["text"] = item["text"]
    elif "body" in item:
        frame_item["text"] = item["body"]
    else:
        raise Exception("no text or body")

    dict_item[frame_item["id"]] = frame_item
    if "comments" in item:
        for comment in item["comments"]:
            dict_item.update(collect_dict_item(comment))
    if "replies" in item:
        for reply in item["replies"]:
            dict_item.update(collect_dict_item(reply))
    return dict_item


def main():
    with open("config_scrape_reddit.json", "r") as file:
        config = json.load(file)
    reddit_dao = RedditDaoDisk("temp/reddit")

    list_profile = reddit_dao.profile.load_all()
    print(f"profile count {len(list_profile)}")
    dict_item = {}
    for profile in list_profile:
        for item in profile["list_item"]:
            dict_item.update(collect_dict_item(item))

    print(f"item_count {len(dict_item)}")

    # create pandas dataframe
    import pandas as pd

    df = pd.DataFrame(list(dict_item.values()))
    df.to_csv("list_item.csv")


if __name__ == "__main__":
    main()
