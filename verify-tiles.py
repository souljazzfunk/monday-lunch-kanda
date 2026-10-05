#!/usr/bin/env python3
"""Verify monday-lunch-map tile config cannot ship banned providers."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
TILES_PATH = ROOT / "tiles.json"
INDEX_PATH = ROOT / "index.html"
SAMPLE_Z, SAMPLE_X, SAMPLE_Y = 12, 3637, 1614
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REFERER = "file:///tmp/index.html"
RUNTIME_KEYS = ("provider", "urlTemplate", "subdomains", "attribution", "maxZoom")


def load_tiles() -> dict:
    return json.loads(TILES_PATH.read_text())


def banned_list(tiles: dict) -> list[str]:
    banned = tiles.get("bannedHostSubstrings") or []
    if not isinstance(banned, list) or not banned:
        raise SystemExit("tiles.json missing bannedHostSubstrings")
    return [str(x) for x in banned]


def find_banned(text: str, banned: list[str]) -> list[str]:
    return [b for b in banned if b in text]


def expand_sample_url(url_template: str, subdomains: list[str]) -> str:
    url = url_template
    if "{s}" in url:
        if not subdomains:
            raise SystemExit("urlTemplate uses {s} but subdomains is empty")
        url = url.replace("{s}", subdomains[0])
    return (
        url.replace("{z}", str(SAMPLE_Z))
        .replace("{x}", str(SAMPLE_X))
        .replace("{y}", str(SAMPLE_Y))
        .replace("{r}", "")
    )


def check_html(html_path: Path, banned: list[str]) -> None:
    text = html_path.read_text()
    hits = find_banned(text, banned)
    if hits:
        raise SystemExit(
            f"FAIL: {html_path} contains banned host substring(s): {', '.join(hits)}"
        )


def check_url_template(tiles: dict, banned: list[str]) -> str:
    url_template = tiles["urlTemplate"]
    hits = find_banned(url_template, banned)
    if hits:
        raise SystemExit(
            f"FAIL: urlTemplate uses banned host substring(s): {', '.join(hits)}"
        )
    sample = expand_sample_url(url_template, list(tiles.get("subdomains") or []))
    hits = find_banned(sample, banned)
    if hits:
        raise SystemExit(
            f"FAIL: sample tile URL uses banned host substring(s): {', '.join(hits)}"
        )
    return sample


def fetch_sample(sample_url: str) -> None:
    req = urllib.request.Request(
        sample_url,
        headers={"User-Agent": BROWSER_UA, "Referer": REFERER},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            ctype = (resp.headers.get("Content-Type") or "").lower()
            body = resp.read(64)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"FAIL: sample tile HTTP {e.code} for {sample_url}") from e
    except Exception as e:
        raise SystemExit(f"FAIL: sample tile request error for {sample_url}: {e}") from e
    if status != 200:
        raise SystemExit(f"FAIL: sample tile HTTP {status} for {sample_url}")
    if not ctype.startswith("image/"):
        raise SystemExit(
            f"FAIL: sample tile Content-Type not image/* ({ctype!r}) for {sample_url}"
        )
    if not body:
        raise SystemExit(f"FAIL: sample tile empty body for {sample_url}")


def verify_project() -> None:
    tiles = load_tiles()
    banned = banned_list(tiles)
    check_html(INDEX_PATH, banned)
    sample = check_url_template(tiles, banned)
    html = INDEX_PATH.read_text()
    m = re.search(
        r'<script type="application/json" id="tiles">(.*?)</script>', html, re.S
    )
    if not m:
        raise SystemExit("FAIL: index.html missing embedded #tiles JSON")
    embedded = json.loads(m.group(1))
    if embedded.get("urlTemplate") != tiles["urlTemplate"]:
        raise SystemExit("FAIL: embedded #tiles urlTemplate != tiles.json")
    if "bannedHostSubstrings" in embedded:
        raise SystemExit(
            "FAIL: embedded #tiles must not include bannedHostSubstrings "
            "(would false-positive the ban check)"
        )
    for b in banned:
        if b in embedded.get("urlTemplate", ""):
            raise SystemExit(f"FAIL: embedded urlTemplate banned: {b}")
    fetch_sample(sample)
    print("PASS: verify-tiles.py")
    print(f"  provider: {tiles.get('provider')}")
    print(f"  sample: {sample}")


def verify_fixture(fixture: Path) -> None:
    tiles = load_tiles()
    banned = banned_list(tiles)
    try:
        check_html(fixture, banned)
    except SystemExit as e:
        msg = str(e)
        if not msg.startswith("FAIL:"):
            raise
        named = [b for b in banned if b in msg]
        if not named:
            raise SystemExit(
                f"FAIL: fixture rejection did not name a banned host: {msg}"
            )
        print(msg)
        print(f"PASS: fixture correctly rejected ({fixture})")
        return
    raise SystemExit(f"FAIL: expected fixture to be rejected: {fixture}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--fixture",
        type=Path,
        help="HTML fixture that must FAIL because it contains a banned host",
    )
    args = ap.parse_args()
    if args.fixture:
        verify_fixture(args.fixture.resolve())
    else:
        verify_project()


if __name__ == "__main__":
    main()
