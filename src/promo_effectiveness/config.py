"""Secure configuration and read-only PostgreSQL connection helpers."""

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


@dataclass(frozen=True)
class DatabaseConfig:
    """Connection settings; the password is excluded from repr and logs."""

    username: str
    password: str = field(repr=False)
    database: str = "retail_analytics"
    host: str = "127.0.0.1"
    port: int = 5432


def load_database_config(env_path: Path) -> DatabaseConfig:
    """Load required credentials without echoing any secret values."""

    path = Path(env_path)
    if not path.is_file():
        raise FileNotFoundError("The configured database environment file is missing")
    values = dotenv_values(path)
    required = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise ValueError("Missing required database settings: " + ", ".join(missing))

    port_value = values.get("POSTGRES_PORT") or "5432"
    if not str(port_value).isascii() or not str(port_value).isdecimal():
        raise ValueError("POSTGRES_PORT must be an integer from 1 to 65535")
    port = int(port_value)
    if not 1 <= port <= 65535:
        raise ValueError("POSTGRES_PORT must be an integer from 1 to 65535")

    return DatabaseConfig(
        username=str(values["POSTGRES_USER"]),
        password=str(values["POSTGRES_PASSWORD"]),
        database=str(values["POSTGRES_DB"]),
        host=str(values.get("POSTGRES_HOST") or "127.0.0.1"),
        port=port,
    )


def create_readonly_engine(config: DatabaseConfig) -> Engine:
    """Create an engine whose PostgreSQL sessions default to read-only."""

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=config.username,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 5,
            "options": "-c default_transaction_read_only=on",
        },
    )


@contextmanager
def readonly_connection(engine: Engine) -> Iterator:
    """Open a transaction that explicitly rejects database writes."""

    with engine.connect() as connection:
        connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        yield connection


def verify_readonly(engine: Engine) -> bool:
    """Return whether the connected PostgreSQL transaction is read-only."""

    with readonly_connection(engine) as connection:
        return connection.execute(text("SHOW transaction_read_only")).scalar_one() == "on"
