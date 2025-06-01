from __future__ import annotations

import asyncio
import base64
import datetime
import logging
from asyncio import QueueEmpty
from typing import Any

import commons
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
        """Primary logging interface. Each project requires one of these.

        Parameters
        ----------
        name: str
            The name of the logger
        base_url: str
            Your base openobserve URL.

            E.g. `base_url="https://logs.example.com"`
        org: str
            The org to make logs under
        stream: str
            The stream for these logs to be ingested under
        username: str
            The username to use for auth
        password: str
            The password to use for auth
        logs_per_call: int
            How many logs to send per request to your instance.
            Useful to set, so you don't hit things like WAF request
            limits in high throughput environments.

            Note logoo makes as many requests as required
            to exhaust the queue every `poll_time`.

            Defaults to `100`.
        poll_time: datetime.timedelta | float
            How often to send all logs to your instance.

            Defaults to every `30` seconds.
        extra_metadata: dict
            Extra metadata to add to all logs made by this class
        global_metadata: dict
            Extra metadata to add to every log sent to your instance
        """
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
        """Start the log sending task."""
        if self.__task is None:
            self.__task = asyncio.create_task(self._consume())

    async def _consume(self):
        while True:
            try:
                while True:
                    await asyncio.sleep(self.poll_time)

                    while data_queue.qsize() != 0:
                        data_stream = []
                        for _ in range(self.logs_per_call):
                            try:
                                data = data_queue.get_nowait()
                                if self.global_metadata is not None:
                                    data = {**data, **self.global_metadata}

                                data_stream.append(data)
                                data_queue.task_done()
                            except QueueEmpty:
                                break

                        log.debug(
                            "Attempting to send %s logs to %s instance",
                            len(data_stream),
                            self.__url,
                        )

                        resp: httpx.Response = await self.__client.post(
                            self.__url,
                            content=orjson.dumps(data_stream),  # type: ignore
                        )
                        del data_stream

                        if resp.status_code != 200:
                            log.error(
                                "Failed to send logs to host with status code %s and response %s",
                                resp.status_code,
                                resp.text,
                            )
                            continue

                        resp_body = resp.json()
                        if resp_body.get("code") == 200:
                            for stream in resp_body.get("status", []):
                                success = int(stream.get("successful", 0))
                                failure = int(stream.get("failed", 0))
                                log.debug(
                                    "Sent %s logs to stream %s. %s successful, %s failed%s",
                                    success + failure,
                                    stream.get("name"),
                                    success,
                                    failure,
                                    f'\n\tError: {stream.get("error")}' if stream.get("error") is not None else ""
                                )

                        else:
                            log.error("Something went wrong uploading logs: %s", resp_body)

            except Exception as e:
                log.critical(
                    "Something went wrong in the dispatcher which caused it to crash.\n%s",
                    commons.exception_as_string(e),
                )
            finally:
                await self.__client.aclose()
                self.__client: httpx.AsyncClient = httpx.AsyncClient(
                    headers=self.__headers,
                )
                log.debug("Reconfigured new instance client")
