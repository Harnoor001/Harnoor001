"""Pull live GitHub numbers into data/github.json (runs daily in Actions).

Contribution days come from the public calendar fragment that the profile
page itself loads, so no token is needed. Repo counts come from the REST API;
GITHUB_TOKEN is used when present to avoid the anonymous rate limit.
"""

import datetime as dt
import json
import os
import re

import requests
from bs4 import BeautifulSoup

from theme import USER

OUT = "data/github.json"
UA = {"User-Agent": f"{USER}-profile-readme"}


def contributions():
    html = requests.get(f"https://github.com/users/{USER}/contributions", headers=UA, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    counts = {}
    for tip in soup.select("tool-tip"):
        m = re.match(r"(\d+|No) contributions?", tip.get_text(strip=True))
        if m and tip.get("for"):
            counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append(
            {
                "date": td["data-date"],
                "level": int(td.get("data-level", 0)),
                "count": counts.get(td.get("id"), 0),
            }
        )
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup may have changed")
    return days


def streaks(days):
    today = dt.date.today().isoformat()
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # the current streak survives a quiet *today* (the day isn't over yet)
    current = 0
    for d in reversed([d for d in days if d["date"] <= today]):
        if d["count"]:
            current += 1
        elif d["date"] == today and current == 0:
            continue
        else:
            break
    return current, longest


def repos():
    headers = dict(UA)
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    user = requests.get(f"https://api.github.com/users/{USER}", headers=headers, timeout=30).json()
    return {"public_repos": user.get("public_repos", 0), "followers": user.get("followers", 0)}


def main():
    days = contributions()
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    data = {
        "updated": dt.date.today().isoformat(),
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"]),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        **repos(),
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1)
    print(
        f"{data['total']} contributions, {data['active_days']} active days, "
        f"streak {current} (best {longest}), {data['public_repos']} repos"
    )


if __name__ == "__main__":
    main()
