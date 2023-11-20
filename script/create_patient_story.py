import asyncio
import json
import os
from typing import Dict, List

from arin_apify.reddit_dao_mongo import RedditDaoMongo
from arin_openai.client_openai import ClientOpenai


def find_best(dict_instance: Dict[str, List[dict]], list_instance_id: List[str], list_subreddit: List[str]):
    dict_content_size = {}
    for instance_id in list_instance_id:
        if instance_id not in dict_instance:
            continue
        for item in dict_instance[instance_id]:
            if item["subreddit"] in list_subreddit:
                if instance_id not in dict_content_size:
                    dict_content_size[instance_id] = 0
                dict_content_size[instance_id] += len(item["content"])
    list_content_size_sorted = sorted(dict_content_size.items(), key=lambda item: item[1], reverse=True)
    print(list_content_size_sorted[:10])


async def main():
    # Replace these values with your actual database and collection names
    scrape_id = "scrape_flu"
    instance_id = "Silly_Account_7317"
    disease = "the flu"
    path_file_dict_instance_gathered = f"dict_instance_gathered_{scrape_id}.json"
    path_file_dict_instance_selected = f"dict_instance_selected_{scrape_id}.json"
    connection_string: str = os.getenv("ARIN_APIFY_MONGO_CONNECTIONSTRING")  # type: ignore
    database_name = "arin-apify"
    dao_mongo = RedditDaoMongo(connection_string, database_name)
    scrape_config = await dao_mongo.scrape_config.load(scrape_id)
    with open(path_file_dict_instance_selected, "r") as file:
        dict_instance = json.load(file)

    with open("dict_label.json", "r") as file:
        dict_label = json.load(file)
    list_instance_candidate = []

    for instance_id_temp, label in dict_label.items():
        if label:
            list_instance_candidate.append(instance_id_temp)
    instance = dict_instance[instance_id]
    content_string = ""

    if instance_id not in dict_instance:
        print("instance not found in dict_instance")
        find_best(dict_instance, list_instance_candidate, scrape_config["list_subreddit_source"])
        exit()

    if instance_id not in list_instance_candidate:
        print("instance not found in list_instance_candidate")
        find_best(dict_instance, list_instance_candidate, scrape_config["list_subreddit_source"])
        exit()
    for item in instance:
        if item["subreddit"] in scrape_config["list_subreddit_source"]:
            content_string += item["content"]
    if len(content_string) == 0:
        find_best(dict_instance, list_instance_candidate, scrape_config["list_subreddit_source"])
        exit()

    content_string = content_string[:30000]
    client = ClientOpenai.from_default_azure("gpt-4", do_cache=False)
    print(client.engine_name)

    chat_completion = client.chat_completion_messages(
        [
            {"role": "system", "content": "You are a helpful assistant. "},
            {
                "role": "user",
                "content": f"Write a story about a patient with {disease} using the following information: {content_string}",
            },
        ],
    )

    print(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
