import hashlib
from calendar import c


def compute_sha256(object_id: str):
    sha256 = hashlib.sha256()
    sha256.update(object_id.encode())
    return sha256.hexdigest()


def unwrap_content(instance_dict: dict):
    list_content_instance = []
    for instance in instance_dict["list_item"]:
        content_instance = {}
        content_instance["id"] = instance["id"]
        content_instance["type"] = instance["type"]
        content_instance["author"] = instance["author"]
        content_instance["subreddit"] = instance["subreddit"]
        content_instance["created_at"] = instance["createdAt"]
        if instance["type"] == "comment":
            content_instance["content"] = instance["body"]
        elif instance["type"] == "post":
            content_instance["content"] = instance["text"]

        else:
            print(instance.keys())
            raise RuntimeError(f"unknown type {instance['type']}")

        list_content_instance.append(content_instance)
        if "list_item" in instance:
            list_content_instance.extend(unwrap_content(instance))
    return list_content_instance
