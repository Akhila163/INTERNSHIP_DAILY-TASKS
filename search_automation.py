"""
day9_search_automation
-----------------------
Runs a batch of Google dorks automatically and logs the results to a file,
instead of typing each dork into the browser by hand.

Two backends are supported:

1. "cse"    - Google Programmable Search Engine (official API, needs an API
              key + a Search Engine ID). Reliable, rate-limited by Google,
              recommended for anything beyond a handful of one-off queries.

2. "scrape" - the `googlesearch-python` package, which scrapes results
              directly from google.com. No key needed, but it is unofficial,
              easy to get rate-limited / captcha'd on, and technically
              against Google's Terms of Service for anything but light,
              personal use. Use small delays and small result counts.

Usage:
    python search_automation.py --backend cse --dorks dorks.txt
    python search_automation.py --backend scrape --dorks dorks.txt

Config for the CSE backend can be passed via environment variables
(GOOGLE_CSE_API_KEY, GOOGLE_CSE_CX) or edited directly in config.py.
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import config

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_dorks(path: str) -> list[str]:
    """Read one dork per line from a text file, skipping blanks/comments."""
    dorks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                dorks.append(line)
    return dorks


def search_scrape(query: str, num_results: int = 10) -> list[dict]:
    """Backend: googlesearch-python (unofficial scraping, no API key)."""
    from googlesearch import search as gsearch

    results = []
    try:
        # advanced=True returns SearchResult objects with title/description
        for r in gsearch(query, num_results=num_results, advanced=True, sleep_interval=2):
            results.append(
                {
                    "title": getattr(r, "title", ""),
                    "url": getattr(r, "url", str(r)),
                    "description": getattr(r, "description", ""),
                }
            )
    except Exception as e:
        results.append({"error": str(e)})
    return results


def search_cse(query: str, num_results: int = 10) -> list[dict]:
    """Backend: Google Programmable Search Engine (official API)."""
    import requests

    api_key = config.GOOGLE_CSE_API_KEY
    cx = config.GOOGLE_CSE_CX

    if not api_key or not cx:
        return [{"error": "Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_CX in config.py / env vars"}]

    results = []
    # The API returns max 10 results per request; page through with 'start'
    fetched = 0
    start = 1
    while fetched < num_results:
        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "start": start,
            "num": min(10, num_results - fetched),
        }
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
        if resp.status_code != 200:
            results.append({"error": f"HTTP {resp.status_code}: {resp.text[:200]}"})
            break
        data = resp.json()
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                }
            )
        fetched += len(items)
        start += len(items)
        if len(items) < params["num"]:
            break  # no more pages
        time.sleep(config.REQUEST_DELAY_SECONDS)
    return results


BACKENDS = {
    "scrape": search_scrape,
    "cse": search_cse,
}


def run_batch(dorks: list[str], backend: str, num_results: int) -> list[dict]:
    search_fn = BACKENDS[backend]
    all_results = []
    for i, dork in enumerate(dorks, start=1):
        print(f"[{i}/{len(dorks)}] Running: {dork}")
        results = search_fn(dork, num_results=num_results)
        all_results.append(
            {
                "dork": dork,
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "result_count": len(results),
                "results": results,
            }
        )
        if backend == "scrape":
            time.sleep(config.REQUEST_DELAY_SECONDS)  # be polite / avoid blocks
    return all_results


def write_logs(all_results: list[dict], backend: str) -> tuple[Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"results_{backend}_{stamp}.json"
    txt_path = OUTPUT_DIR / f"results_{backend}_{stamp}.log"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Search automation run — backend: {backend} — {stamp}\n")
        f.write("=" * 70 + "\n\n")
        for entry in all_results:
            f.write(f"DORK: {entry['dork']}\n")
            f.write(f"Time: {entry['timestamp']}  |  Results: {entry['result_count']}\n")
            f.write("-" * 70 + "\n")
            for r in entry["results"]:
                if "error" in r:
                    f.write(f"  [ERROR] {r['error']}\n")
                    continue
                f.write(f"  * {r['title']}\n")
                f.write(f"    {r['url']}\n")
                if r.get("description"):
                    f.write(f"    {r['description']}\n")
                f.write("\n")
            f.write("\n")

    return json_path, txt_path


def main():
    parser = argparse.ArgumentParser(description="Run a batch of Google dorks and log results.")
    parser.add_argument("--dorks", default="dorks.txt", help="Path to a text file, one dork per line")
    parser.add_argument("--backend", choices=list(BACKENDS.keys()), default="scrape")
    parser.add_argument("--num-results", type=int, default=5, help="Results per dork")
    args = parser.parse_args()

    dorks = load_dorks(args.dorks)
    if not dorks:
        print(f"No dorks found in {args.dorks}")
        sys.exit(1)

    all_results = run_batch(dorks, args.backend, args.num_results)
    json_path, txt_path = write_logs(all_results, args.backend)

    print(f"\nDone. {len(dorks)} dorks run.")
    print(f"Log:  {txt_path}")
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
