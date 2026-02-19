# cloud_sync.py

import aiohttp
import asyncio
from typing import Optional


class CloudSync:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session: Optional[aiohttp.ClientSession] = None

    async def ensure_session(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def upload_file(self, filepath: str) -> int:
        await self.ensure_session()

        assert self.session is not None  # helps type checker

        with open(filepath, "rb") as f:
            data = f.read()

        async with self.session.post(
            self.endpoint,
            data={"file": data},
        ) as resp:
            return resp.status

    async def upload_batch(self, files: list[str]):
        tasks = [self.upload_file(f) for f in files]
        return await asyncio.gather(*tasks)

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None
