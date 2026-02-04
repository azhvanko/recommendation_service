import csv
import logging
from datetime import date
from pathlib import Path

import clickhouse_connect

from .config import get_config

__all__ = (
    "close_clickhouse_client",
    "get_clickhouse_async_client",
    "init_clickhouse_client",
    "insert_user_events",
)

logger = logging.getLogger(__name__)

CLICKHOUSE_CLIENT: clickhouse_connect.driver.AsyncClient | None = None


async def init_clickhouse_client() -> None:
    global CLICKHOUSE_CLIENT
    config = get_config()
    CLICKHOUSE_CLIENT = await clickhouse_connect.get_async_client(
        dsn=config.clickhouse_dsn.unicode_string()
    )


async def close_clickhouse_client() -> None:
    global CLICKHOUSE_CLIENT
    if CLICKHOUSE_CLIENT:
        await CLICKHOUSE_CLIENT.close()


async def get_clickhouse_async_client() -> clickhouse_connect.driver.AsyncClient:
    global CLICKHOUSE_CLIENT
    if not CLICKHOUSE_CLIENT:
        await init_clickhouse_client()
    return CLICKHOUSE_CLIENT


def insert_user_events(filename: str = "test.csv", chunk_size: int = 50_000) -> None:
    base_dir = Path("/app/data/")
    csv_file_path = base_dir / filename
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV file not found: `{csv_file_path}`")
    config = get_config()
    clickhouse_client = clickhouse_connect.get_client(dsn=config.clickhouse_dsn.unicode_string())
    batch = []
    total_inserted = 0
    column_names = ["uid", "pid", "brand", "date", "click", "add_to_cart", "purchase"]
    try:
        with open(csv_file_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            logger.info("Start loading data...")
            for row in csv_reader:
                batch.append(
                    (
                        int(row["uid"]),
                        int(row["pid"]),
                        row["brand"].strip(),
                        date.fromisoformat(row["date"]),
                        int(row["click"]),
                        int(row["add_to_cart"]),
                        int(row["purchase"]),
                    )
                )
                if len(batch) >= chunk_size:
                    clickhouse_client.insert(
                        "user_events",
                        batch,
                        column_names=column_names,
                    )
                    total_inserted += len(batch)
                    batch.clear()
            if batch:
                clickhouse_client.insert(
                    "user_events",
                    batch,
                    column_names=column_names,
                )
                total_inserted += len(batch)
                logger.info(f"Finished. Total inserted: {total_inserted}")
    finally:
        clickhouse_client.close()
