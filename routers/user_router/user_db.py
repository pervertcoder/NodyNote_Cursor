from database.db_pool import get_connection


def check_register_duplicates(username: str, email: str) -> dict[str, bool]:
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s) AS username_exists, EXISTS(SELECT 1 FROM users WHERE email = %s) AS email_exists"
        param = (username, email)
        cur.execute(sql, param)
        row = cur.fetchone()
        return {
            "username": bool(row["username_exists"]),
            "email": bool(row["email_exists"]),
        }
    finally:
        cur.close()
        conn.close()


def insert_user(username: str, email: str, password_hash: str, color: str | None = None) -> int:

    conn = get_connection()
    cur = conn.cursor()
    try:
        if color:
            sql = "INSERT INTO users (username, email, password_hash, color) VALUES (%s, %s, %s, %s)"
            param = (username, email, password_hash, color)
        else:
            sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
            param = (username, email, password_hash)
        cur.execute(sql, param)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
