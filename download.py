#!/usr/bin/env python

import argparse
import asyncio
import pathlib

from slack_emoji.download_emoji import download_emoji
from slack_emoji.emoji_dict import get_emoji_dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="download emoji", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-t", "--token", required=True, dest="token", type=str, help="slack token to retrive installed emoji list"
    )
    parser.add_argument(
        "-d", dest="dest_dir", type=pathlib.Path, default=pathlib.Path("./download"), help="download dir"
    )
    args = parser.parse_args()
    return args


async def main() -> None:
    options = parse_args()
    print(options)
    print(await download_emoji(options.dest_dir))
    # emoji_dict = get_emoji_dict(options.token)
    # print(emoji_dict)


if __name__ in "__main__":
    asyncio.run(main())
