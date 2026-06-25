from flask import Flask, render_template, jsonify
import feedparser
import hashlib
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "news.db"


# ----------------------------
# INIT DB (CACHE LAYER)
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
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# RISK ENGINE (RETAIL FOCUS)
# ----------------------------
def calculate_risk(title: str):
    t = title.lower()

    high_keywords = [
        "war", "attack", "death", "earthquake", "crisis",
        "collapse", "recession", "bankrupt", "fire", "explosion",
        "inflation", "price surge", "energy crisis", "shortage",
        "aldi", "lidl", "rewe", "edeka", "kaufland",
        "food prices", "food inflation", "price war",
        "store closure", "supply shortage", "coffee", "milk", "bread"
    ]

    medium_keywords = [
        "policy", "government", "economy", "market",
        "finance", "business", "trade", "tax",
        "company", "merger", "investment"
    ]

    score = 0

    for w in high_keywords:
        if w in t:
            score += 3

    for w in medium_keywords:
        if w in t:
            score += 1

    if score >= 3:
        return "HIGH"
    elif score >= 1:
        return "MEDIUM"
    else:
        return "LOW"


# ----------------------------
# RSS SOURCES (SCALED)
# ----------------------------
RSS_FEEDS = [
    "https://www.tagesschau.de/xml/rss2/",
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
    "https://www.deutschlandfunk.de/rss",
    "https://www.n-tv.de/rss",
    "https://www.spiegel.de/schlagzeilen/index.rss",
]


# ----------------------------
# HASH FOR DEDUP
# ----------------------------
def make_id(title, link):
    raw = title + link
    return hashlib.md5(raw.encode()).hexdigest()


# ----------------------------
# FETCH + SCALE + DEDUP + CACHE
# ----------------------------
def fetch_articles(limit_per_feed=30):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    new_articles = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:limit_per_feed]:
                title = entry.get("title", "No title")
                link = entry.get("link", "#")
                pubDate = entry.get("published", "")

                uid = make_id(title, link)
                risk = calculate_risk(title)

                # check duplicate
                c.execute("SELECT id FROM articles WHERE id=?", (uid,))
                if c.fetchone():
                    continue

                article = (
                    uid,
                    title,
                    link,
                    pubDate,
                    url,
                    risk,
                    datetime.utcnow().isoformat()
                )

                c.execute("""
                    INSERT INTO articles VALUES (?,?,?,?,?,?,?)
                """, article)

                new_articles.append({
                    "title": title,
                    "link": link,
                    "pubDate": pubDate,
                    "source": url,
                    "risk": risk
                })

        except Exception as e:
            print(f"RSS error: {url} -> {e}")

    conn.commit()

    # return latest 200 cached articles
    c.execute("""
        SELECT title, link, pubDate, source, risk
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
            "risk": r[4]
        }
        for r in rows
    ]


# ----------------------------
# API
# ----------------------------
@app.route("/api/retail-news-page")
def retail_news_page():
    articles = fetch_articles()

    return jsonify({
        "page": 1,
        "total": len(articles),
        "articles": articles
    })


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)