"""Image search and download utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

import requests
from duckduckgo_search import DDGS


class ImageDownloader:
    """Search and download images for a word."""

    def __init__(self, headers: dict | None = None) -> None:
        if headers is None:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
                    "Gecko/20100101 Firefox/124.0"
                )
            }
        self.headers = headers

    def search(self, keyword: str) -> list[dict]:
        results = DDGS(headers=self.headers).images(keywords=keyword)
        return results[:3]

    def download(self, keyword: str, home_dir: str) -> List[str]:
        images = self.search(keyword)
        image_paths: List[str] = []
        path = Path(home_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        for i, image in enumerate(images):
            try:
                resp = requests.get(image["image"], stream=True, timeout=8, verify=True)
                if resp.status_code == 200:
                    extension = "." + image["image"].split(".")[-1]
                    if len(extension) <= 5:
                        filepath = path / f"{keyword}{i}{extension}"
                        with filepath.open("wb") as f:
                            f.write(resp.content)
                        # remove leading '.' to keep Flask path usage
                        image_paths.append(str(filepath)[1:])
            except Exception as exc:  # pragma: no cover - network safety
                print(exc)
        return image_paths


# Backwards compatibility

def download_images(keyword: str, home_dir: str) -> list[str]:
    return ImageDownloader().download(keyword, home_dir)
