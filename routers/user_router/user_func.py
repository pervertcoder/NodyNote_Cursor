from datetime import datetime, timedelta
import secrets
import bcrypt

from routers.user_router.user_db import check_register_duplicates, insert_user, insert_session


class User:
    SESSION_EXPIRE_DAYS = 7

    def __init__(self, user_id: int, username: str, email: str, created_at: datetime):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = created_at

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    @staticmethod
    def check_register_duplicates(username: str, email: str) -> dict[str, bool]:
        return check_register_duplicates(username, email)

    @classmethod
    def register(cls, username: str, email: str, password: str, color: str | None = None) -> dict:
        password_hash = cls.hash_password(password)
        user_id = insert_user(username, email, password_hash, color)
        return {"id": user_id, "username": username, "email": email}

    @classmethod
    def create_session(cls, user_id: int, user_agent: str | None = None) -> dict:
        session_id = secrets.token_hex(32)
        expires_at = datetime.now() + timedelta(days=cls.SESSION_EXPIRE_DAYS)
        insert_session(session_id, user_id, expires_at, user_agent)
        return {"session_id": session_id, "expires_at": expires_at}
