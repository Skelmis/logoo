## Logoo
#### A log ingestion engine for [openobserve](https://github.com/openobserve/openobserve)

*Pronounced log-ew*

`pip install logoo`

### Examples

Primary file. One instance of `PrimaryLogger` is required per program.
```python
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
    logger.critical("Something went wrong!")
    await asyncio.sleep(10)


asyncio.run(main())
```

Any other file:
```python
from logoo import Logger

logger = Logger(__name__)
logger.info("This comes from another file.")
```

Documentation is as follows and remarkably simple:
```text
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

    Defaults to `100`.
poll_time: datetime.timedelta | float
    How often to send all logs to your instance.

    Defaults to every `30` seconds.
extra_metadata: dict
    Extra metadata to add to all logs made by this class
global_metadata: dict
    Extra metadata to add to every log sent to your instance
```

---

### Support

Want realtime help? Join the discord [here](https://discord.gg/BqPNSH2jPg).

---

### License
This project is licensed under the MIT license