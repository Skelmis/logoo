import asyncio

from logoo import PrimaryLogger


async def main():
    logger: PrimaryLogger = PrimaryLogger(
        __name__,
        base_url="",
        org="",
        stream="",
        username="",
        password="",
        poll_time=5,
    )
    await logger.start_consumer()

    logger.info("Hello world!")
    await asyncio.sleep(10)


asyncio.run(main())
