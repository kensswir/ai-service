import sqlite3

conn = sqlite3.connect("news.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    link TEXT,
    ai_result TEXT
)
""")

conn.commit()

print("Database ready!")