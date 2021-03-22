import asyncio
import os
import pathlib
import zipfile
from typing import Dict

import aiohttp
import yaml


async def download_emoji(dest_dir: pathlib.Path, registed_emoji_dict: Dict[str, str]) -> None:
    limit = 128
    sem = asyncio.Semaphore(limit)

    await get_slack_emoji_from_asserts_dir(sem, dest_dir, registed_emoji_dict)
    await get_party_parrot(sem, dest_dir, registed_emoji_dict)


async def get_slack_emoji_from_asserts_dir(
    sem: asyncio.Semaphore, dest_dir: pathlib.Path, registed_emoji_dict: Dict[str, str]
) -> None:
    emoji_dict = get_emoji_dict()

    coros = []
    for name, uri in emoji_dict.items():
        if name.split("/")[1] in registed_emoji_dict:
            print(f"{name} is already registered")
            continue

        target = dest_dir / f"{name}{pathlib.Path(uri).suffix}"
        if not target.parent.exists():
            target.parent.mkdir(parents=True)

        coros.append(download_single_file(sem, target, uri))

    await asyncio.gather(*coros)


async def get_party_parrot(sem: asyncio.Semaphore, dest_dir: pathlib.Path, registed_emoji_dict: Dict[str, str]) -> None:
    uri = "https://cultofthepartyparrot.com/parrots-56e80e9d0e.zip"
    target = dest_dir / "parrot.zip"
    await download_single_file(sem, target, uri)
    with zipfile.ZipFile(target) as existing_zip:
        existing_zip.extractall(dest_dir)

    dirs = ((dest_dir / "parrots"), (dest_dir / "parrots" / "hd"))
    for d in dirs:
        assert d.exists(), f"{d} not found..."
        for fname in d.iterdir():
            if not fname.is_file():
                continue
            name = fname.stem
            if name in registed_emoji_dict:
                print(f"{name} is already registered")
                os.remove(fname.absolute())


def get_emoji_dict() -> Dict[str, str]:
    assets_dir = pathlib.Path(__file__).absolute().parents[1] / "assets" / "emojipacks" / "packs"
    assert assets_dir.exists()

    white_list = ["slackmojis-logo.yaml", "octicons.yaml", "nekoatsume.yaml", "frontend.yaml"]

    emoji_dict = {}

    for name in white_list:
        fname = assets_dir / name
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
