LOAN_COLUMNS = "id, student_id, item_id, quantity, status, created_at"


def create(db, student_id, item_id, quantity, status, created_at):
    cursor = db.execute(
        """
        INSERT INTO loans (student_id, item_id, quantity, status, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (student_id, item_id, quantity, status, created_at),
    )
    return cursor.lastrowid


def get_by_id(db, loan_id):
    query = f"SELECT {LOAN_COLUMNS} FROM loans WHERE id = ?"
    return db.execute(query, (loan_id,)).fetchone()


def mark_returned(db, loan_id):
    """Mark a BORROWED loan as RETURNED; return affected row count."""
    cursor = db.execute(
        "UPDATE loans SET status = 'RETURNED' WHERE id = ? AND status = 'BORROWED'",
        (loan_id,),
    )
    return cursor.rowcount


def list_by_student(db, student_id):
    query = f"""
        SELECT {LOAN_COLUMNS}
        FROM loans
        WHERE student_id = ?
        ORDER BY created_at DESC, id DESC
    """
    return db.execute(query, (student_id,)).fetchall()
