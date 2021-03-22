from typing import Dict, cast

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_emoji_dict(token: str) -> Dict[str, str]:
    client = WebClient(token=token)
    try:
        response = client.emoji_list()
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        print("Got an error: ", e)
        raise e

    return cast(Dict[str, str], response.get("emoji"))
