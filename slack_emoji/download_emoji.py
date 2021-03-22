import asyncio
import pathlib
from typing import Dict

import aiohttp
import yaml


async def download_emoji(dest_dir: pathlib.Path, registed_emoji_dict) -> None:
    emoji_dict = get_emoji_dict()

    limit = 128
    sem = asyncio.Semaphore(limit)

    coros = []
    for name, uri in emoji_dict.items():
        if name in registed_emoji_dict:
            print(f"{name} is already registered")
            continue

        target = dest_dir / f"{name}{pathlib.Path(uri).suffix}"
        if not target.parent.exists():
            target.parent.mkdir(parents=True)

        coros.append(download_single_file(sem, target, uri))

    await asyncio.gather(*coros)


def get_emoji_dict() -> Dict[str, str]:
    assets_dir = pathlib.Path(__file__).absolute().parents[1] / "assets" / "emojipacks" / "packs"
    assert assets_dir.exists()

    emoji_dict = {}

    for fname in assets_dir.iterdir():
        with open(fname, "r") as f:
            config = yaml.safe_load(f)
            for emoji in config["emojis"]:
                key = pathlib.Path(pathlib.Path(fname.name).stem) / str(emoji["name"])
                emoji_dict[str(key)] = emoji["src"]

    return emoji_dict


async def download_single_file(
    sem: asyncio.Semaphore,
    dest: pathlib.Path,
    uri: str,
) -> None:
    async with sem:
        print(dest, "is running")
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as resp:
                if resp.status == 200:
                    with open(dest, "wb") as f:
                        f.write(await resp.read())
                        f.close()
