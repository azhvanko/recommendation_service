import click

from ..clickhouse import insert_user_events as _insert_user_events


@click.group()
def cli() -> None:
    pass


@cli.command("insert_user_events")
@click.option("--filename", type=str, default=None, show_default=False)
@click.option("--chunk-size", type=int, default=None, show_default=False)
def insert_user_events(filename: str | None, chunk_size: int | None) -> None:
    kwargs = {}
    if filename is not None:
        kwargs["filename"] = filename
    if chunk_size is not None:
        kwargs["chunk_size"] = chunk_size
    _insert_user_events(**kwargs)
