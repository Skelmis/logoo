import asyncio
import base64
import datetime
import logging
from asyncio import QueueEmpty
from typing import Any

import httpx
import orjson

from logoo import Logger
from logoo.data import data_queue

log = logging.getLogger(__name__)


class PrimaryLogger(Logger):
    def __init__(
        self,
        name: str,
        *,
        base_url: str,
        org: str,
        stream: str,
        username: str,
        password: str,
        logs_per_call: int = 100,
        poll_time: datetime.timedelta | float = datetime.timedelta(seconds=30),
        extra_metadata: dict[Any, Any] | None = None,
        global_metadata: dict[Any, Any] | None = None,
    ):
        super().__init__(name, extra_metadata)
        self.__headers: dict[str, str] = {
            "Content-type": "application/json",
            "Authorization": "Basic "
            + base64.b64encode(bytes(username + ":" + password, "utf-8")).decode(
                "utf-8"
            ),
        }
        self.__url: str = f"{base_url}/api/{org}/{stream}/_json"
        self.__client: httpx.AsyncClient = httpx.AsyncClient(
            headers=self.__headers,
        )
        self.logs_per_call: int = logs_per_call
        self.poll_time: float = (
            poll_time.total_seconds()
            if isinstance(poll_time, datetime.timedelta)
            else poll_time
        )

        # This differs to extra_metadata as we include this in ALL logs
        self.global_metadata: dict[Any, Any] | None = global_metadata

        self.__task: asyncio.Task | None = None

    async def start_consumer(self):
        if self.__task is None:
            self.__task = asyncio.create_task(self._consume())

    async def _consume(self):
        while True:
            await asyncio.sleep(self.poll_time)

            data_stream = []
            for _ in range(self.logs_per_call):
                try:
                    data_stream.append(data_queue.get_nowait())
                except QueueEmpty:
                    break

            resp: httpx.Response = await self.__client.post(
                self.__url,
                data=orjson.dumps(data_stream),  # type: ignore
            )
            del data_stream

            if resp.status_code != 200:
                log.error(
                    "Failed to send logs to host with status code %s",
                    resp.status_code,
                )
                return

            # TODO Read json reponse body and check successful vs failed
