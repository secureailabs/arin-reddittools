import asyncio
import hashlib
import json
import os

from arin_apify.reddit_dao_mongo import RedditDaoMongo

from arin_reddittools.tools_reddit import compute_sha256, unwrap_content


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_all"
    path_file_dict_instance_gathered = f"dict_instance_gathered_{scrape_id}.json"
    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    connection_string: str = os.getenv("ARIN_APIFY_MONGO_CONNECTIONSTRING")  # type: ignore
    database_name = "arin-apify"
    dao_mongo = RedditDaoMongo(connection_string, database_name)
    scrape_config = await dao_mongo.scrape_config.load(scrape_id)
    scrape_state = await dao_mongo.scrape_state.load(scrape_id)

    if not os.path.exists(path_file_dict_instance_gathered):
        # Get all keys from the specified collection

        list_object_id = [compute_sha256(username) for username in scrape_state["dict_user_closed"].keys()]
        dict_instance_gathered = await dao_mongo.profile.load_many_dict(list_object_id, True)
        with open(path_file_dict_instance_gathered, "w") as file:
            json.dump(dict_instance_gathered, file)
    else:
        with open(path_file_dict_instance_gathered, "r") as file:
            dict_instance_gathered = json.load(file)

    dict_user_content = {}
    for instance in dict_instance_gathered.values():
        list_content_instance = unwrap_content(instance)
        for content_instance in list_content_instance:
            author = content_instance["author"]
            if author not in dict_user_content:
                dict_user_content[author] = []
            dict_user_content[author].append(content_instance)

    dict_instance_selected = {}
    for username, list_content_instance in dict_user_content.items():
        for content_instance in list_content_instance:
            if content_instance["subreddit"] in scrape_config["list_subreddit_source"]:
                dict_instance_selected[username] = list_content_instance
                break

    dict_subreddit_count = {}
    for instance in dict_instance_selected.values():
        for item in instance:
            if item["subreddit"] not in dict_subreddit_count:
                dict_subreddit_count[item["subreddit"]] = 0
            dict_subreddit_count[item["subreddit"]] += 1
    # sort
    list_subreddit_count_sorted = sorted(dict_subreddit_count.items(), key=lambda item: item[1], reverse=True)
    for subreddit, count in list_subreddit_count_sorted[:60]:
        if subreddit not in scrape_config["list_subreddit_source"]:
            print(f"{subreddit}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
