#!/usr/bin/env python3
"""Perbarui news.json dari GDELT DOC 2.0 API (gratis, tanpa kunci API).

Jalankan: python scripts/update_news.py
Hanya library standar Python. Jika satu titik gagal atau tidak ada hasil,
entri lamanya dipertahankan. Jika semua gagal, file tidak ditulis ulang.
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "news.json")
API = "https://api.gdeltproject.org/api/v2/doc/doc"
MAX_PER_SPOT = 3
TIMESPAN = "14d"
SLEEP = 6  # GDELT meminta jeda antar-permintaan

# Query per titik konflik (sintaks GDELT: frasa dalam tanda kutip, OR dalam kurung).
QUERIES = {
    "hormuz": '("Strait of Hormuz" OR Hormuz) (Iran OR CENTCOM) sourcelang:english',
    "yanbu": '(Yanbu OR "East-West pipeline") Saudi sourcelang:english',
    "bab": '(Houthi OR "Bab el-Mandeb" OR "Red Sea") (ship OR shipping OR attack) sourcelang:english',
    "saratov": '(refinery OR Saratov) (Ukraine OR Ukrainian) drone Russia sourcelang:english',
    "novo": '(Novorossiysk OR "Black Sea") (port OR grain OR terminal) sourcelang:english',
    "donbas": '(Ukraine OR Kyiv) (energy OR "power grid" OR talks OR Donbas) Russia sourcelang:english',
    "kalin": '(Kaliningrad OR Baltic) (NATO OR Russia) sourcelang:english',
    "israel": '(Gaza OR Lebanon OR Hezbollah) Israel (strike OR ceasefire) sourcelang:english',
    "taiwan": '("Taiwan Strait" OR Taiwan) (China OR PLA) (drills OR military) sourcelang:english',
    "venez": 'Venezuela (oil OR PDVSA OR Chevron) sourcelang:english',
}


def fetch(query):
    params = urllib.parse.urlencode({
        "query": query, "mode": "artlist", "format": "json",
        "maxrecords": "25", "timespan": TIMESPAN, "sort": "datedesc",
    })
    req = urllib.request.Request(API + "?" + params, headers={"User-Agent": "war-market-sim-news/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def transform(data, limit=MAX_PER_SPOT):
    """Ubah respons GDELT jadi daftar entri; satu entri per judul, terbaru dulu."""
    out, seen = [], set()
    for a in data.get("articles", []):
        title = " ".join((a.get("title") or "").split())
        url = a.get("url") or ""
        if not title or not url.startswith("http"):
            continue
        key = title.lower()[:60]
        if key in seen:
            continue
        seen.add(key)
        sd = a.get("seendate", "")  # 20261115T083000Z
        try:
            date = datetime.strptime(sd, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
        except ValueError:
            continue
        out.append({"date": date, "title": title, "title_en": title,
                    "source": a.get("domain") or "", "url": url})
        if len(out) >= limit:
            break
    return out


def main():
    try:
        with open(OUT, encoding="utf-8") as f:
            old = json.load(f).get("items", {})
    except (OSError, ValueError):
        old = {}
    items, ok = dict(old), 0
    for i, (sid, q) in enumerate(QUERIES.items()):
        if i:
            time.sleep(SLEEP)
        try:
            got = transform(fetch(q))
        except Exception as e:  # jaringan, JSON rusak, dll.
            print(f"[{sid}] gagal: {e}", file=sys.stderr)
            continue
        if got:
            items[sid] = got
            ok += 1
            print(f"[{sid}] {len(got)} berita")
        else:
            print(f"[{sid}] tidak ada hasil, entri lama dipertahankan")
    if ok == 0:
        print("Semua titik gagal; news.json tidak diubah.", file=sys.stderr)
        sys.exit(1)
    payload = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "items": items}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
