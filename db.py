
import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv() 

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


pool = pooling.MySQLConnectionPool(
    pool_name="message_board_pool",
    pool_size=5,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

def get_conn():
    return pool.get_connection()
