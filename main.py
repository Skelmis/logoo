import asyncio
import logging
import os

from logoo import PrimaryLogger

logging.basicConfig(level=logging.WARNING)
logging.getLogger("logoo").setLevel(logging.DEBUG)


async def main():
    logger: PrimaryLogger = PrimaryLogger(
        __name__,
        base_url=os.environ["URL"],
        org=os.environ['ORG'],
        stream=os.environ['STREAM'],
        username=os.environ['USER'],
        password=os.environ['PASS'],
        poll_time=5,
    )
    await logger.start_consumer()

    logger.info("Hello world!")
    await asyncio.sleep(10)


asyncio.run(main())
