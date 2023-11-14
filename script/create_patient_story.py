import asyncio
import json
import os

from arin_apify.reddit_dao_mongo import RedditDaoMongo
from openapi import openapi

from arin_reddittools.instance_discoverer import InstanceDiscoverer
from arin_reddittools.tools_reddit import compute_sha256


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_hpv"
    openapi
    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    with open(path_file_dict_instance_selected, "r") as file:
        dict_instance = json.load(file)
    instance = dict_instance["OkIndependence2701"]
    content_string = ""
    for item in instance:
        if item["subreddit"] == "HPV":
            content_string += item["content"]


if __name__ == "__main__":
    asyncio.run(main())
