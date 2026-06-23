from flask import Flask, render_template
import requests
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

NODE_API = "http://localhost:3000/api/retail-news-page?page=1"

# ================= DB =================

def db():
    return sqlite3.connect("news.db")

def init():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        link TEXT,
        ai TEXT
    )
    """)

    conn.commit()
    conn.close()

def get(title):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT ai FROM news WHERE title=?", (title,))
    r = c.fetchone()
    conn.close()
    return r

def save(title, link, ai):
    conn = db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO news VALUES (NULL,?,?,?)", (title, link, ai))
    conn.commit()
    conn.close()

# ================= AI =================

def classify(text):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Return Category and Severity (LOW/MEDIUM/HIGH)."},
                {"role":"user","content":text}
            ]
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        print("AI error:", e)
        return "Category: Neutral | Severity: LOW"

def score(ai):
    if "HIGH" in ai: return 3
    if "MEDIUM" in ai: return 2
    return 1

# ================= DATA =================

def load():
    try:
        r = requests.get(NODE_API, timeout=10)
        data = r.json()
        return data.get("articles", [])
    except Exception as e:
        print("Node API error:", e)
        return []

# ================= ROUTE =================

@app.route("/")
def home():

    items = []

    for a in load():

        title = a.get("title", "")
        link = a.get("link", "")

        cached = get(title)

        if cached:
            ai = cached[0]
        else:
            ai = classify(title)
            save(title, link, ai)

        items.append({
            "title": title,
            "link": link,
            "ai": ai
        })

    items.sort(key=lambda x: score(x["ai"]), reverse=True)

    return render_template("dashboard.html", items=items)

if __name__ == "__main__":
    init()
    app.run(port=5050, debug=True)