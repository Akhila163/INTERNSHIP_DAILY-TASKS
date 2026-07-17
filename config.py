"""
Configuration for search_automation.py

For the "cse" backend, get these from:
  - API key:   https://console.cloud.google.com/apis/credentials
  - Search Engine ID (cx): https://programmablesearchengine.google.com/
    (create a search engine, set it to "Search the entire web")

Prefer environment variables over hardcoding real keys in this file,
especially if this folder is ever committed to git.
"""

import os

GOOGLE_CSE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY", "")
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX", "")

# Delay between requests, in seconds. Keep this at 2+ for the "scrape"
# backend to reduce the chance of getting rate-limited or captcha'd.
REQUEST_DELAY_SECONDS = 2
