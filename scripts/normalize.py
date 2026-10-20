#!/usr/bin/env python3
"""Turn the Loop Habit Tracker export ("raw data/") into data/habits.csv and data/<year>/*.csv."""
import csv
import glob
import os
import shutil
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw data")
DATA = os.path.join(ROOT, "data")

# Loop's checkmark values -> ours. YES_AUTO is a day Loop counts as kept because the
# habit's target for that week/month is already met; UNKNOWN is a day nothing was marked.
VALUES = {"YES_MANUAL": "done", "YES_AUTO": "auto", "NO": "no", "UNKNOWN": ""}


def main():
    habits = list(csv.DictReader(open(os.path.join(RAW, "Habits.csv"))))
    # The combined file ends on the export day; per-habit files run ahead with auto-filled days.
    export_day = max(r["Date"] for r in csv.DictReader(open(os.path.join(RAW, "Checkmarks.csv"))))

    checks, scores, meta = defaultdict(dict), defaultdict(dict), []
    for hb in habits:
        folder = os.path.join(RAW, f"{hb['Position']} {hb['Name']}")
        marks = {r["Date"]: VALUES[r["Value"]] for r in csv.DictReader(open(os.path.join(folder, "Checkmarks.csv")))
                 if r["Date"] <= export_day}
        for d, v in marks.items():
            checks[d][hb["Name"]] = v
        for r in csv.DictReader(open(os.path.join(folder, "Scores.csv"))):
            if r["Date"] <= export_day:
                scores[r["Date"]][hb["Name"]] = r["Score"]
        meta.append({"position": int(hb["Position"]), "name": hb["Name"], "color": hb["Color"],
                     "times": hb["FrequencyNumerator"], "per_days": hb["FrequencyDenominator"],
                     "start": min(marks), "archived": hb["Archived?"]})

    names = [m["name"] for m in meta]
    for d in glob.glob(os.path.join(DATA, "[0-9]" * 4)):
        shutil.rmtree(d)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "habits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(meta[0]))
        w.writeheader()
        w.writerows(meta)

    def write(table, name):
        by_year = defaultdict(list)
        for d in sorted(table):
            by_year[d[:4]].append([d] + [table[d].get(n, "") for n in names])
        for y, rows in by_year.items():
            os.makedirs(os.path.join(DATA, y), exist_ok=True)
            with open(os.path.join(DATA, y, name + ".csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date"] + names)
                w.writerows(rows)
        return by_year

    years = write(checks, "checkmarks")
    write(scores, "scores")
    done = sum(v == "done" for day in checks.values() for v in day.values())
    print(f"data/: {len(meta)} habits, {len(checks)} days ({min(checks)} → {export_day}), "
          f"{done} check-ins, years {min(years)}–{max(years)}")


if __name__ == "__main__":
    main()
