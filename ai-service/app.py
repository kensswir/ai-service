from flask import Flask, render_template, jsonify
import feedparser
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)

DB = "news.db"


# ----------------------------
# INIT DB
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            pubDate TEXT,
            source TEXT,
            risk TEXT,
            type TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ----------------------------
# RSS FEEDS (FOOD SAFETY + RETAIL GERMANY)
# ----------------------------
RSS_FEEDS = [
    "https://www.lebensmittelwarnung.de/bvl-lmw-de/opensaga/feed.xml",
    "https://www.foodwatch.org/de/rss.xml",
    "https://www.tagesschau.de/xml/rss2/",
    "https://www.spiegel.de/schlagzeilen/index.rss",
    "https://www.n-tv.de/rss"
]


# ----------------------------
# ID
# ----------------------------
def make_id(title, link):
    return hashlib.md5((title + link).encode()).hexdigest()


# ----------------------------
# RISK ENGINE (FOOD SAFETY FOCUS)
# ----------------------------
def calculate_risk(title: str):
    t = title.lower()

    high = [
        "recall", "warning", "withdrawal", "contamination",
        "listeria", "salmonella", "food poisoning",
        "risk", "danger", "outbreak"
    ]

    retail = ["aldi", "lidl", "rewe", "edeka", "promotion", "offer"]

    complaint = ["complaint", "lawsuit", "investigation", "customer"]

    score = 0

    for w in high:
        if w in t:
            score += 4

    for w in retail:
        if w in t:
            score += 2

    for w in complaint:
        if w in t:
            score += 1

    if score >= 6:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def classify_type(title):
    t = title.lower()

    if any(x in t for x in ["recall", "withdrawal", "warning", "contamination"]):
        return "RECALL"

    if any(x in t for x in ["aldi", "lidl", "rewe", "edeka", "promotion", "offer"]):
        return "RETAIL"

    if any(x in t for x in ["complaint", "lawsuit", "investigation"]):
        return "COMPLAINT"

    return "NEWS"


# ----------------------------
# FETCH NEWS
# ----------------------------
def fetch_articles(limit=30):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    articles = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                pubDate = entry.get("published", "")

                uid = make_id(title, link)
                risk = calculate_risk(title)
                type_ = classify_type(title)

                c.execute("SELECT id FROM articles WHERE id=?", (uid,))
                if c.fetchone():
                    continue

                c.execute("""
                    INSERT INTO articles VALUES (?,?,?,?,?,?,?,?)
                """, (
                    uid,
                    title,
                    link,
                    pubDate,
                    url,
                    risk,
                    type_,
                    datetime.utcnow().isoformat()
                ))

                articles.append({
                    "title": title,
                    "link": link,
                    "pubDate": pubDate,
                    "source": url,
                    "risk": risk,
                    "type": type_
                })

        except Exception as e:
            print("RSS error:", url, e)

    conn.commit()

    c.execute("""
        SELECT title, link, pubDate, source, risk, type
        FROM articles
        ORDER BY created_at DESC
        LIMIT 200
    """)

    rows = c.fetchall()
    conn.close()

    return [
        {
            "title": r[0],
            "link": r[1],
            "pubDate": r[2],
            "source": r[3],
            "risk": r[4],
            "type": r[5]
        }
        for r in rows
    ]


# ----------------------------
# API
# ----------------------------
@app.route("/api/news")
def api_news():
    articles = fetch_articles()

    return jsonify({
        "total": len(articles),
        "food_recall": [a for a in articles if a["type"] == "RECALL"],
        "retail": [a for a in articles if a["type"] == "RETAIL"],
        "complaints": [a for a in articles if a["type"] == "COMPLAINT"],
        "all": articles
    })


# ----------------------------
# UI
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)