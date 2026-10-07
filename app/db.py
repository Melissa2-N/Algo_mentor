from __future__ import annotations

import psycopg_pool

from .config import settings

_pool: psycopg_pool.ConnectionPool | None = None


def get_pool() -> psycopg_pool.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg_pool.ConnectionPool(
            settings.database_url, min_size=1, max_size=8, open=True
        )
    return _pool


def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    with get_pool().connection() as conn:
        cur = conn.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_one(query: str, params: tuple = ()) -> dict | None:
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query: str, params: tuple = ()) -> None:
    with get_pool().connection() as conn:
        conn.execute(query, params)
        conn.commit()
