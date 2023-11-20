import asyncio
import json
import os

from arin_apify.reddit_dao_mongo import RedditDaoMongo

from arin_reddittools.instance_discoverer import InstanceDiscoverer
from arin_reddittools.tools_reddit import compute_sha256


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_flu"
    discover_id = "discover_user_flu"

    connection_string: str = os.getenv("ARIN_APIFY_MONGO_CONNECTIONSTRING")  # type: ignore
    database_name = "arin-apify"
    dao_mongo = RedditDaoMongo(connection_string, database_name)

    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    with open(path_file_dict_instance_selected, "r") as file:
        dict_instance = json.load(file)

    discoverer = InstanceDiscoverer(dao_mongo, scrape_id, discover_id, dict_instance, ["flu"])
    await discoverer.loop()


if __name__ == "__main__":
    asyncio.run(main())
