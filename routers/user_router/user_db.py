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

# 登入用：以 email 查詢 user
def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT id, username, email, password_hash, color, created_at
        FROM users
        WHERE email = %s
        LIMIT 1
        """
        param = (email,)
        cur.execute(sql, param)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

# 每次驗證用：以 user_id 查詢 user 的公開資料
def get_user_public_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT id, username, email, color, created_at
        FROM users
        WHERE id = %s
        LIMIT 1
        """
        param = (user_id,)
        cur.execute(sql, param)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def insert_session(session_id: str, user_id: int, expires_at, user_agent: str | None = None) -> None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = "INSERT INTO sessions (session_id, user_id, expires_at, user_agent) VALUES (%s, %s, %s, %s)"
        param = (session_id, user_id, expires_at, user_agent)
        cur.execute(sql, param)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def get_session_by_session_id(session_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT session_id, user_id, expires_at, created_at, user_agent
        FROM sessions
        WHERE session_id = %s AND expires_at > NOW()
        LIMIT 1
        """
        param = (session_id,)
        cur.execute(sql, param)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_user_id_by_session_id(session_id: str) -> int | None:
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = "SELECT user_id FROM sessions WHERE session_id = %s AND expires_at > NOW()"
        param = (session_id,)
        cur.execute(sql, param)
        row = cur.fetchone()
        if not row:
            return None
        return int(row["user_id"])
    finally:
        cur.close()
        conn.close()


def delete_session(session_id: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = "DELETE FROM sessions WHERE session_id = %s"
        param = (session_id,)
        cur.execute(sql, param)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def delete_sessions_by_user_id(user_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = "DELETE FROM sessions WHERE user_id = %s"
        param = (user_id,)
        cur.execute(sql, param)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
