import asyncio
import json
import os

from arin_apify.reddit_dao_mongo import RedditDaoMongo

from arin_reddittools.instance_discoverer import InstanceDiscoverer
from arin_reddittools.tools_reddit import compute_sha256


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_hpv"

    connection_string: str = os.getenv("ARIN_APIFY_MONGO_CONNECTIONSTRING")  # type: ignore
    database_name = "arin-apify"
    dao_mongo = RedditDaoMongo(connection_string, database_name)
    scrape_config = await dao_mongo.scrape_config.load(scrape_id)
    list_username_source = scrape_config["list_username_source"]

    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    with open(path_file_dict_instance_selected, "r") as file:
        dict_instance = json.load(file)

    with open("dict_label.json", "r") as file:
        dict_label = json.load(file)
    with open("dict_skip.json", "r") as file:
        dict_skip = json.load(file)

    for username in list_username_source:
        dict_label[username] = True

    discoverer = InstanceDiscoverer(dict_instance, dict_label, dict_skip)

    discoverer.loop()


if __name__ == "__main__":
    asyncio.run(main())
