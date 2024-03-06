import asyncio
from dataclasses import dataclass, field
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


SKIP = ["https://pja.mykhi.org/generatory2.0", "https://pja.mykhi.org/generatory2.0", "https://pja.mykhi.org/upload", "https://pja.mykhi.org/upload/", "https://pja.mykhi.org/mgr/", "https://pja.mykhi.org/upload/?C=M;O=A"]


class Scraper:
    def __init__(self, config: Config):
        self.config = config

        self.data = Directory(url=config.URL, name=config.URL)

    async def download_file(self, file: File, directory_path: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(file.url) as response:
                if response.status == 200:
                    # Ensure the directory exists
                    os.makedirs(directory_path, exist_ok=True)

                    file_path = os.path.join(directory_path, file.name)
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    logging.info(f"Downloaded {file.url} to {file_path}")
                else:
                    logging.error(f"Failed to download {file.url}: Status {response.status}")

    async def _get_all_links(self, driver, url: str):
        await driver.get(url)

        elements = await driver.find_elements(By.XPATH, "//a[@href]")
        hrefs = [await element.get_attribute("href") for element in elements]
        hrefs = filter(lambda href: href.startswith(url) and href[-1] != "#" and href != url and not href.replace(url, "").startswith("?") and href not in SKIP, hrefs)
        return set(hrefs)

    async def fetch_directory_contents(self, driver, directory: Directory):
        links = await self._get_all_links(driver, directory.url)
        logging.info(f"Found {len(links)} links in {directory.url}")
        logging.info(f"Links: {links}")
        for link in links:
            if self.is_directory(link):
                subdirectory = Directory(url=link, name=link.split('/')[-1], parent=directory)
                directory.directories.append(subdirectory)
                await self.fetch_directory_contents(driver, subdirectory)
            else:
                file_obj = File(url=link, name=link.split('/')[-1], parent=directory)
                directory.files.append(file_obj)

                download_path = os.path.join(settings.DATA_DIRECTORY, directory.name)
                ext = file_obj.name.split('.')[-1]
                if ext in ["pdf", "txt", "csv", "json", "md"]:
                    asyncio.create_task(self.download_file(file_obj, download_path))

    async def run(self):
        options = webdriver.ChromeOptions()
        async with webdriver.Chrome(options=options) as driver:
            await self.fetch_directory_contents(driver, self.data)

        download_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if download_tasks:
            await asyncio.gather(*download_tasks)

        return self.data

    def is_directory(self, url: str) -> bool:
        if "." in url.replace(self.config.URL, ""):
            return False
        return True
