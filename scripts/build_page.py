#!/usr/bin/env python3
"""Build index.html from data/ using scripts/page.html as the template."""
import csv
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# One character per day: done by hand, kept automatically (target already met), marked "no", nothing.
CODES = {"done": "x", "auto": "a", "no": "n", "": "-"}


def rows(name):
    for f in sorted(glob.glob(os.path.join(DATA, "*", name + ".csv"))):
        yield from csv.DictReader(open(f))


def main():
    habits = list(csv.DictReader(open(os.path.join(DATA, "habits.csv"))))
    checks = list(rows("checkmarks"))
    scores = {r["date"]: r for r in rows("scores")}
    start = checks[0]["date"]

    out = []
    for hb in habits:
        n = hb["name"]
        # strength (Loop's score) in % with one decimal, null before the habit starts
        strength = [round(float(scores[r["date"]][n]) * 100, 1) if r["date"] in scores and scores[r["date"]][n] else None
                    for r in checks]
        out.append({"name": n, "times": int(hb["times"]), "per": int(hb["per_days"]), "start": hb["start"],
                    "marks": "".join(CODES[r[n]] for r in checks),
                    "score": [int(v) if v is not None and v.is_integer() else v for v in strength]})

    payload = json.dumps({"start": start, "habits": out}, separators=(",", ":"))
    page = open(os.path.join(ROOT, "scripts", "page.html")).read().replace("__DATA__", payload)
    open(os.path.join(ROOT, "index.html"), "w").write(page)
    done = sum(h["marks"].count("x") for h in out)
    print(f"index.html: {len(out)} habits, {len(checks)} days from {start}, {done} check-ins, {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
