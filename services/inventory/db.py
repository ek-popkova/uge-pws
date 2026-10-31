"""The stock, in a SQLite file instead of a dictionary: it survives a restart."""

import os
import sqlite3

from .data import PRODUCTS

DB_PATH = os.environ.get("INVENTORY_DB", "inventory.db")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dictionaries
    return conn


def init() -> None:
    """Create the table, and fill it with lab 1's products the first time."""
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            " id INTEGER PRIMARY KEY, name TEXT NOT NULL,"
            " price_eur REAL NOT NULL, stock INTEGER NOT NULL)"
        )
        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO products VALUES (:id, :name, :price_eur, :stock)",
                PRODUCTS.values(),
            )


def list_products(in_stock: bool | None, limit: int, offset: int) -> list[dict]:
    sql = "SELECT * FROM products"
    if in_stock is not None:
        sql += " WHERE stock > 0" if in_stock else " WHERE stock = 0"
    sql += " ORDER BY id LIMIT ? OFFSET ?"
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, (limit, offset))]


def get_product(product_id: int) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    return dict(row) if row else None


def create_product(fields: dict) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO products (name, price_eur, stock) VALUES (:name, :price_eur, :stock)",
            fields,
        )
    return cur.lastrowid


def update_product(product_id: int, fields: dict) -> bool:
    """Change the given fields; False if there is no such product."""
    if not fields:
        return get_product(product_id) is not None
    sets = ", ".join(f"{name} = :{name}" for name in fields)
    with connect() as conn:
        cur = conn.execute(f"UPDATE products SET {sets} WHERE id = :id", {**fields, "id": product_id})
    return cur.rowcount == 1


def delete_product(product_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    return cur.rowcount == 1


def reserve(product_id: int, quantity: int) -> bool:
    """Take units out of the stock in one statement, so two orders cannot both get the last one."""
    with connect() as conn:
        cur = conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (quantity, product_id, quantity),
        )
    return cur.rowcount == 1
