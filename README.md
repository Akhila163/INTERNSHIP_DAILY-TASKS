# Day 9 — Search Automation

Runs a list of Google dorks automatically instead of typing each one into
the browser by hand, and logs everything (title, URL, snippet, timestamp)
to a file for later review.

## Files

- `search_automation.py` — main script
- `config.py` — API key / delay settings
- `dorks.txt` — sample list of 10 dorks (one per line, `#` = comment)
- `output/` — where logs land: a human-readable `.log` and a structured `.json` per run

## Two backends

**`scrape`** (default) uses the `googlesearch-python` package, which scrapes
results straight from google.com. No API key needed, but:

- It's unofficial and against Google's Terms of Service for anything beyond
  light personal use.
- Google's bot detection blocks it quickly and reliably. When I actually
  ran the sample batch in `output/`, every query came back
  `403 Client Error: Forbidden` — that's not a bug, it's Google's anti-bot
  wall. This is the expected/common outcome, not an edge case, and the
  sample log shows the script's error handling catching it cleanly rather
  than crashing.
- Useful for understanding the mechanics, not something to rely on for
  real investigation work.

**`cse`** uses the official Google Programmable Search Engine API. This is
the reliable option:

1. Get an API key: https://console.cloud.google.com/apis/credentials
2. Create a search engine at https://programmablesearchengine.google.com/,
   set it to "Search the entire web", and copy its Search Engine ID (`cx`).
3. Set them as environment variables before running:
   ```
   set GOOGLE_CSE_API_KEY=your_key_here      # Windows / PowerShell: $env:GOOGLE_CSE_API_KEY="..."
   set GOOGLE_CSE_CX=your_cx_here
   ```
   (or edit `config.py` directly, but don't commit real keys)
4. Free tier is 100 queries/day; each dork with `--num-results 10` uses one
   query (up to 10 results per request).

## Usage

```
pip install googlesearch-python requests

python search_automation.py --backend scrape --dorks dorks.txt --num-results 5
python search_automation.py --backend cse --dorks dorks.txt --num-results 10
```

Each run writes two timestamped files to `output/`:
- `results_<backend>_<timestamp>.log` — readable summary
- `results_<backend>_<timestamp>.json` — same data, structured, for feeding
  into another script later

## How it works

1. `load_dorks()` reads `dorks.txt` into a list, skipping blank lines/comments.
2. `run_batch()` loops over the dorks, calling the chosen backend's search
   function for each one, with a short delay between requests (politeness /
   avoiding rate limits — configurable in `config.py`).
3. Each backend function returns a plain list of `{title, url, description}`
   dicts, or a `{"error": ...}` dict if something went wrong, so one bad
   query doesn't kill the whole batch.
4. `write_logs()` dumps everything to both a `.log` and a `.json` file with
   timestamps.

## Notes / things to swap in for real use

- Replace the placeholder dorks in `dorks.txt` with the actual dorks for
  whatever investigation this is for.
- If running many dorks on the `cse` backend, watch the 100/day free quota.
- The `scrape` backend is left in mainly as a demonstration of *why* you'd
  want the official API — it's the "before" to `cse`'s "after."
