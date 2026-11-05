import os
import sqlite3

from flask import current_app, g


def get_db():
    """Return the request-scoped SQLite connection, creating it if needed."""
    if "db" not in g:
        database_path = current_app.config["DATABASE"]
        directory = os.path.dirname(database_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        g.db = sqlite3.connect(database_path, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(exception=None):
    """Close the request-scoped database connection, if any."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the database schema if it does not exist yet."""
    db = get_db()
    with current_app.open_resource("schema.sql") as schema_file:
        db.executescript(schema_file.read().decode("utf-8"))
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
