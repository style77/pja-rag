import asyncio
from dataclasses import dataclass, field
import hashlib
import json
import logging
import os
from typing import List, Optional

import aiohttp
from scraper.config import ScraperSettings as Config
from selenium_driverless.types.by import By
from selenium_driverless import webdriver

from scraper import config as settings


@dataclass
class File:
    url: str
    name: str
    parent: Optional["Directory"] = None


@dataclass
class Directory:
    url: str
    name: str
    parent: Optional["Directory"] = None
    files: List["File"] = field(default_factory=list)
    directories: List["Directory"] = field(default_factory=list)


SKIP = [
    "https://pja.mykhi.org/generatory2.0",
    "https://pja.mykhi.org/generatory2.0",
    "https://pja.mykhi.org/upload",
    "https://pja.mykhi.org/upload/",
    "https://pja.mykhi.org/mgr/",
    "https://pja.mykhi.org/upload/?C=M;O=A",
]


class Scraper:
    def __init__(self, config: Config):
        self.config = config

        self.data = Directory(url=config.URL, name=config.URL)

        self.total_downloaded_size = 0
        self.storage_limit = 50 * 1024 * 1024 * 1024
        self.download_queue = asyncio.Queue()

    def update_url_hash_mapping(self, url_hash: str, original_url: str):
        mapping_file = "url_hash_mapping.json"
        try:
            with open(mapping_file, "r") as f:
                mapping = json.load(f)
        except FileNotFoundError:
            mapping = {}

        mapping[url_hash] = original_url

        with open(mapping_file, "w") as f:
            json.dump(mapping, f, indent=4)

    async def download_file(self, file: File, directory_path: str):
        if self.total_downloaded_size > self.storage_limit:
            logging.info(
                f"Storage limit reached: {self.total_downloaded_size} > {self.storage_limit}"
            )
            return

        logging.info(f"Downloading {file.url} to {directory_path}")

        url_hash = hashlib.md5(file.url.encode("utf-8")).hexdigest()[:10]
        async with aiohttp.ClientSession() as session:
            async with session.get(file.url) as response:
                if response.status == 200:
                    os.makedirs(directory_path, exist_ok=True)

                    file_splitted = file.name.split(".")
                    file_ext = file_splitted[-1]
                    file_name = file_splitted[0]

                    file_name_with_hash = f"{file_name}_{url_hash}.{file_ext}"
                    file_path = os.path.join(directory_path, file_name_with_hash)
                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            self.total_downloaded_size += len(chunk)

                            if self.total_downloaded_size > self.storage_limit:
                                logging.info(
                                    f"Storage limit reached: {self.total_downloaded_size} > {self.storage_limit}"
                                )
                                return
                    self.update_url_hash_mapping(url_hash, file.url)
                    logging.info(f"Downloaded {file.url} to {file_path}")
                else:
                    logging.error(
                        f"Failed to download {file.url}: Status {response.status}"
                    )

    async def _get_all_links(self, driver, url: str):
        await driver.get(url)

        elements = await driver.find_elements(By.XPATH, "//a[@href]")
        hrefs = [await element.get_attribute("href") for element in elements]
        hrefs = filter(
            lambda href: href.startswith(url)
            and href[-1] != "#"
            and href != url
            and not href.replace(url, "").startswith("?")
            and href not in SKIP,
            hrefs,
        )
        return set(hrefs)

    async def fetch_directory_contents(self, driver, directory: Directory):
        links = await self._get_all_links(driver, directory.url)
        logging.info(f"Found {len(links)} links in {directory.url}")
        for link in links:
            if link in SKIP:
                continue
            if self.is_directory(link):
                subdirectory = Directory(
                    url=link, name=link.split("/")[-1], parent=directory
                )
                directory.directories.append(subdirectory)
                await self.fetch_directory_contents(driver, subdirectory)
            else:
                file_obj = File(url=link, name=link.split("/")[-1], parent=directory)
                directory.files.append(file_obj)

                download_path = os.path.join(settings.DATA_DIRECTORY, directory.name)
                ext = file_obj.name.split(".")[-1]
                if ext in ["pdf", "txt", "csv", "json", "md"]:
                    logging.info(f"Adding {file_obj.url} to download queue")
                    await self.download_queue.put((file_obj, download_path))

    async def manage_downloads(self):
        try:
            while True:
                if self.download_queue.empty() and self.total_downloaded_size >= self.storage_limit:
                    # If the storage limit is reached and no more items are in the queue, exit gracefully.
                    logging.info("Storage limit reached, stopping download manager.")
                    return
                file, directory_path = await self.download_queue.get()
                await self.download_file(file, directory_path)
                self.download_queue.task_done()
        except asyncio.CancelledError:
            logging.info("Download manager task was cancelled.")

    async def run(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        async with webdriver.Chrome(options=options) as driver:
            download_manager = asyncio.create_task(self.manage_downloads())
            await self.download_queue.join()

            await self.fetch_directory_contents(driver, self.data)

            download_manager.cancel()
            try:
                await download_manager
            except asyncio.CancelledError:
                logging.info("Download manager was cancelled successfully.")

    def is_directory(self, url: str) -> bool:
        if "." in url.replace(self.config.URL, ""):
            return False
        return True
