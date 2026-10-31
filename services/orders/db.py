"""The orders, in a database of their own: Orders never reads Inventory's tables."""

import os
import sqlite3

DB_PATH = os.environ.get("ORDERS_DB", "orders.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            " id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL,"
            " quantity INTEGER NOT NULL, total_eur REAL NOT NULL)"
        )


def create_order(product_id: int, quantity: int, total_eur: float) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO orders (product_id, quantity, total_eur) VALUES (?, ?, ?)",
            (product_id, quantity, total_eur),
        )
    return cur.lastrowid


def get_order(order_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return dict(row) if row else None


def list_orders() -> list[dict]:
    with connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM orders ORDER BY id")]
