ITEM_COLUMNS = "id, name, total_stock, available_stock"


def list_all(db):
    query = f"SELECT {ITEM_COLUMNS} FROM items ORDER BY id"
    return db.execute(query).fetchall()


def get_by_id(db, item_id):
    query = f"SELECT {ITEM_COLUMNS} FROM items WHERE id = ?"
    return db.execute(query, (item_id,)).fetchone()


def create(db, name, total_stock):
    cursor = db.execute(
        "INSERT INTO items (name, total_stock, available_stock) VALUES (?, ?, ?)",
        (name, total_stock, total_stock),
    )
    return cursor.lastrowid


def decrease_available_stock(db, item_id, quantity):
    """Decrease stock only when enough is available; return affected row count."""
    cursor = db.execute(
        """
        UPDATE items
        SET available_stock = available_stock - ?
        WHERE id = ? AND available_stock >= ?
        """,
        (quantity, item_id, quantity),
    )
    return cursor.rowcount


def increase_available_stock(db, item_id, quantity):
    cursor = db.execute(
        "UPDATE items SET available_stock = available_stock + ? WHERE id = ?",
        (quantity, item_id),
    )
    return cursor.rowcount
