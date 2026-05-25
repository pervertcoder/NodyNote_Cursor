from mysql.connector import pooling
from mysql.connector.connection import MySQLConnection

from database.db_setting import DB_POOL_SIZE, get_db_config

_pool: pooling.MySQLConnectionPool | None = None


def _create_pool() -> pooling.MySQLConnectionPool:
    return pooling.MySQLConnectionPool(
        pool_name="nodynote_pool",
        pool_size=DB_POOL_SIZE,
        pool_reset_session=True,
        autocommit=False,
        **get_db_config(),
    )


def get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = _create_pool()
    return _pool


def get_connection() -> MySQLConnection:
    """從連線池取得一條連線；用完請 close() 以歸還池子。"""
    return get_pool().get_connection()
