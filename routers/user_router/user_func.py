from datetime import datetime
import bcrypt

from routers.user_router.user_db import check_register_duplicates, insert_user


class User:
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

    def __init__(self, user_id: int, username: str, password: str, email: str, created_at: datetime):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.created_at = created_at

    def get_user_by_id(self, user_id: int):
        return self.user_id

    def find_user_by_username(self, username: str):
        pass
