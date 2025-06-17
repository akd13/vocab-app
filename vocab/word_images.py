"""Image search and download utilities."""

from __future__ import annotations

import os
import asyncio
import aiohttp
from pathlib import Path
from typing import List
from functools import lru_cache
from duckduckgo_search import DDGS
import random
import time

class ImageDownloader:
    """Search and download images for a word."""

    def __init__(self, headers=None):
        if headers is None:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
        self.headers = headers
        self.session = None
        self._current_keyword = None
        self._user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        self._last_request_time = 0
        self._min_request_interval = 2  # Minimum seconds between requests
        self._max_retries = 3

    async def _wait_for_rate_limit(self):
        """Implement exponential backoff for rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last_request
            # Add some jitter to prevent synchronized requests
            wait_time += random.uniform(0, 1)
            print(f"Rate limit: Waiting {wait_time:.2f} seconds before next request")
            await asyncio.sleep(wait_time)
        
        self._last_request_time = time.time()

    @lru_cache(maxsize=1000)
    async def search(self, keyword, retry_count=0):
        """Search for images with rate limit handling."""
        if retry_count >= self._max_retries:
            print(f"Max retries reached for keyword: {keyword}")
            return []

        try:
            await self._wait_for_rate_limit()
            print(f"Searching for images with keyword: {keyword} (attempt {retry_count + 1})")
            results = DDGS(headers=self.headers).images(keywords=keyword)
            print(f"Found {len(results)} images for {keyword}")
            return results[:10]  # Get more images to have alternatives if some fail
        except Exception as e:
            if "RateLimit" in str(e) or "403" in str(e):
                print(f"Rate limit hit for {keyword}, retrying in {2 ** retry_count} seconds...")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.search(keyword, retry_count + 1)
            print(f"Error searching images for {keyword}: {e}")
            return []

    async def _download_image(self, session, image_url, filepath, retry_count=0):
        if retry_count >= len(self._user_agents):
            print(f"All retry attempts failed for {image_url}")
            return None

        try:
            await self._wait_for_rate_limit()
            print(f"Attempting to download image from: {image_url} (attempt {retry_count + 1})")
            headers = self.headers.copy()
            headers["User-Agent"] = self._user_agents[retry_count]
            
            async with session.get(image_url, headers=headers, timeout=8) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    with filepath.open("wb") as f:
                        f.write(content)
                    print(f"Successfully downloaded image to: {filepath.name}")
                    return filepath.name
                elif resp.status in [403, 429]:  # Forbidden or Too Many Requests
                    print(f"Access forbidden/rate limited for {image_url}, retrying with different user agent...")
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    return await self._download_image(session, image_url, filepath, retry_count + 1)
                else:
                    print(f"Failed to download image. Status code: {resp.status}")
        except Exception as exc:
            print(f"Error downloading image {image_url}: {exc}")
            if retry_count < len(self._user_agents) - 1:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._download_image(session, image_url, filepath, retry_count + 1)
        return None

    async def _download_images_async(self, images, path):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        tasks = []
        for i, image in enumerate(images):
            extension = os.path.splitext(image["image"])[1].lower()
            if not extension or len(extension) > 5:
                extension = ".jpg"
            filename = f"{self._current_keyword}{i+1}{extension}"
            filepath = path / filename
            print(f"Creating download task for: {filename}")
            task = self._download_image(self.session, image["image"], filepath)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        successful_downloads = [r for r in results if r is not None]
        print(f"Successfully downloaded {len(successful_downloads)} images for {self._current_keyword}")
        return successful_downloads[:3]  # Return only the first 3 successful downloads

    async def download_async(self, keyword, home_dir):
        """Download images for a word."""
        self._current_keyword = keyword
        path = Path(home_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        # Search for images with rate limit handling
        images = await self.search(keyword)
        if not images:
            print(f"No images found for {keyword}")
            return []
        
        # Download images
        return await self._download_images_async(images, path)

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """Cleanup when the object is deleted."""
        if self.session:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception:
                pass

# Backwards compatibility
def download_images(keyword, home_dir):
    return ImageDownloader().download(keyword, home_dir)
