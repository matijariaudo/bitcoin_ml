
import os
import sqlite3

DB_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
DB_FILE_PATH = f'{DB_PATH}database{os.sep}database.db'
print("CHEQUEANDO LA BD --->",DB_FILE_PATH)  # Ver ruta completa

#### codigo nuevo### (creación de tablas de suscriptores y envíos)
with sqlite3.connect(DB_FILE_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha REAL UNIQUE,
        precio REAL NOT NULL,
        precio_min_4h REAL NOT NULL,
        prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),
        probability REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        status INTEGER NOT NULL DEFAULT 1
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sent_emails (
        id_email INTEGER PRIMARY KEY AUTOINCREMENT,
        subscriber_id INTEGER NOT NULL,
        sent_at REAL NOT NULL,
        FOREIGN KEY (subscriber_id) REFERENCES subscribers(id)
    )
    """)
    conn.commit()
# ### fin codigo nuevo###