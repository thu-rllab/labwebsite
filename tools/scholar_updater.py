#!/usr/bin/env python3
"""
tools/scholar_updater.py
========================
Auto-fetch papers from lab members' publication profiles and update
final_all_papers.json with newly discovered papers.

Default backend: Semantic Scholar API (accessible in China, no proxy needed).
Fallback backend: Google Scholar (requires VPN / proxy outside China).

Usage (run from the tools/ directory):
    python scholar_updater.py                         # Semantic Scholar, all members
    python scholar_updater.py --dry-run               # preview without saving
    python scholar_updater.py --author "Yun Qu"       # only one member
    python scholar_updater.py --max-pubs 20           # only N most recent papers

    # Google Scholar backend (requires VPN):
    python scholar_updater.py --backend scholar
    python scholar_updater.py --backend scholar --delay 5
    python scholar_updater.py --backend scholar --scraper-api-key YOUR_KEY

Requirements:
    pip install semanticscholar          # for default Semantic Scholar backend
    pip install scholarly                # for --backend scholar only

Notes
-----
- Newly added entries have "nan" for code_url, demo_url, tag.
  Review and fill these before running publications_to_html.py.
- Semantic Scholar searches by member name; if a member has a common name
  and gets the wrong match, add a "semantic_scholar_id" field to their entry
  in final_all_members.json with their numeric Semantic Scholar author ID.
  Example: "semantic_scholar_id": "2262347"
- Xiang Li(2026-5-20): Scholar backend seems to be better. 
  Semantic Scholar backend fails to find all new papers and sometimes returns invalid names.
"""

import argparse
import json
import re
import sys
import time
from typing import List, Optional, Tuple

# ── Venue normalisation table ──────────────────────────────────────────────────
VENUE_NORMALISE = {
    # NeurIPS
    "advances in neural information processing": "NeurIPS",
    "neural information processing systems": "NeurIPS",
    "neurips": "NeurIPS",
    "nips": "NeurIPS",
    # ICML
    "international conference on machine learning": "ICML",
    "icml": "ICML",
    # ICLR
    "international conference on learning representations": "ICLR",
    "iclr": "ICLR",
    # CVPR / ICCV / ECCV
    "computer vision and pattern recognition": "CVPR",
    "cvpr": "CVPR",
    "international conference on computer vision": "ICCV",
    "iccv": "ICCV",
    "european conference on computer vision": "ECCV",
    "eccv": "ECCV",
    # AAAI
    "aaai conference on artificial intelligence": "AAAI",
    "aaai": "AAAI",
    # KDD
    "knowledge discovery and data mining": "KDD",
    "kdd": "KDD",
    # COLT / AISTATS
    "conference on learning theory": "COLT",
    "colt": "COLT",
    "aistats": "AISTATS",
    "artificial intelligence and statistics": "AISTATS",
    # ACL family
    "association for computational linguistics": "ACL",
    "acl": "ACL",
    "empirical methods in natural language": "EMNLP",
    "emnlp": "EMNLP",
    # arXiv
    "arxiv": "arXiv",
    "preprint": "arXiv",
    "corr": "arXiv",
}


def _normalise_venue(raw: str) -> str:
    """Best-effort venue normalisation. Returns raw string if nothing matches."""
    if not raw:
        return "arXiv"
    low = raw.lower().strip()
    for keyword, canonical in VENUE_NORMALISE.items():
        if keyword in low:
            return canonical
    return raw.strip()


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def _save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
# Semantic Scholar backend (default — works in China)
# ══════════════════════════════════════════════════════════════════════════════

_SS_FIELDS = [
    "title", "year", "venue", "authors",
    "openAccessPdf", "url", "externalIds",
]


def _fetch_pubs_semantic(name: str, semantic_id: Optional[str], max_pubs: int = 0) -> list:
    """Fetch publications from Semantic Scholar API.

    If semantic_id is provided (numeric string from the member JSON), it is used
    directly.  Otherwise the author is looked up by name — the first result is
    taken, which is usually correct for distinctive names.  For common names,
    set 'semantic_scholar_id' in final_all_members.json to pin the right author.
    """
    try:
        from semanticscholar import SemanticScholar
    except ImportError:
        print("ERROR: `semanticscholar` not installed.  Run: pip install semanticscholar")
        return []

    sch = SemanticScholar()

    print(f"  → Fetching papers (semantic_id={semantic_id}) …")
    try:
        papers = sch.get_author_papers(semantic_id, fields=_SS_FIELDS)
        papers = list(papers)
    except Exception as exc:
        print(f"    ERROR fetching papers: {exc}")
        return []

    print(f"    Found {len(papers)} papers.")
    if max_pubs > 0 and len(papers) > max_pubs:
        papers = papers[:max_pubs]
        print(f"    Limited to first {max_pubs} (--max-pubs).")
    return papers


def _semantic_pub_to_entry(paper, fallback_author: str) -> Tuple[Optional[str], Optional[list]]:
    """Convert a Semantic Scholar Paper object to (title, JSON-entry)."""
    title = (getattr(paper, "title", None) or "").strip()
    if not title:
        return None, None

    year = str(getattr(paper, "year", None) or "nan")

    raw_venue = (getattr(paper, "venue", None) or "").strip()
    venue_name = _normalise_venue(raw_venue)
    venue_full = f"{venue_name} {year}".strip() if year != "nan" else venue_name

    # Full author list
    authors_list = getattr(paper, "authors", None) or []
    if authors_list:
        authors = ", ".join(
            a.name for a in authors_list if getattr(a, "name", None)
        )
    else:
        authors = fallback_author

    # URL: prefer arXiv link, then open-access PDF, then Semantic Scholar page
    ext = getattr(paper, "externalIds", None) or {}
    arxiv_id = ext.get("ArXiv")
    oa = getattr(paper, "openAccessPdf", None) or {}
    oa_url = oa.get("url") if isinstance(oa, dict) else getattr(oa, "url", None)
    sem_url = getattr(paper, "url", None)

    if arxiv_id:
        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
    elif oa_url:
        paper_url = oa_url
    elif sem_url:
        paper_url = sem_url
    else:
        paper_url = "nan"

    entry = [year, venue_full, authors, paper_url, "nan", "nan", "nan"]
    return title, entry


# ══════════════════════════════════════════════════════════════════════════════
# Google Scholar backend (requires VPN / proxy outside China)
# ══════════════════════════════════════════════════════════════════════════════

def _extract_scholar_id(url: str) -> Optional[str]:
    m = re.search(r"user=([A-Za-z0-9_\-]+)", url or "")
    return m.group(1) if m else None


def _fetch_pubs_scholar(scholar_id: str, name: str,
                        fill_delay: float = 3.0, max_pubs: int = 0) -> list:
    """Fetch publications via the scholarly library (Google Scholar scraper)."""
    from scholarly import scholarly as sch

    print(f"  → Step 1/3: searching author profile for {name} …")
    try:
        author = sch.search_author_id(scholar_id)
    except Exception as exc:
        print(f"    ERROR at search_author_id: {exc}")
        return []

    print(f"  → Step 2/3: filling publication list …")
    try:
        author = sch.fill(author, sections=["publications"])
        pubs = author.get("publications", [])
        print(f"    Found {len(pubs)} publication records.")
    except Exception as exc:
        print(f"    ERROR at fill(author): {exc}")
        return []

    if max_pubs > 0:
        pubs = pubs[:max_pubs]
        print(f"    Limited to first {len(pubs)} records (--max-pubs {max_pubs}).")

    print(f"  → Step 3/3: filling details for each publication …")
    filled = []
    for i, pub in enumerate(pubs):
        title_preview = pub.get("bib", {}).get("title", "?")[:50]
        print(f"    [{i+1}/{len(pubs)}] {title_preview} …")
        try:
            filled.append(sch.fill(pub))
        except Exception as exc:
            print(f"    WARNING: could not fill pub #{i+1} — {exc}. Using shallow record.")
            filled.append(pub)
        if fill_delay > 0:
            time.sleep(fill_delay)

    print(f"    Done. Filled {len(filled)} records.")
    return filled


def _scholar_pub_to_entry(pub: dict, fallback_author: str) -> Tuple[Optional[str], Optional[list]]:
    """Convert a scholarly pub dict to (title, JSON-entry)."""
    bib = pub.get("bib", {})
    title = bib.get("title", "").strip()
    if not title:
        return None, None

    year = str(bib.get("pub_year", bib.get("year", "nan")))

    raw_venue = (
        bib.get("venue", "")
        or bib.get("journal", "")
        or bib.get("booktitle", "")
        or bib.get("conference", "")
        or ""
    )
    venue_name = _normalise_venue(raw_venue)
    venue_full = f"{venue_name} {year}".strip() if year != "nan" else venue_name

    raw_authors = bib.get("author", fallback_author)
    authors = raw_authors.replace(" and ", ", ").strip()

    paper_url = pub.get("pub_url") or pub.get("eprint_url") or "nan"

    entry = [year, venue_full, authors, paper_url, "nan", "nan", "nan"]
    return title, entry


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch new papers and update final_all_papers.json"
    )
    parser.add_argument(
        "--backend", choices=["semantic", "scholar"], default="semantic",
        help="Data source: 'semantic' = Semantic Scholar API (default, works in China); "
             "'scholar' = Google Scholar (requires VPN)."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be added without modifying any files."
    )
    parser.add_argument(
        "--author", default=None,
        help="Only fetch for the member whose name contains this substring (case-insensitive)."
    )
    parser.add_argument(
        "--max-pubs", type=int, default=0,
        help="Only process the N most recent publications per author (0 = all)."
    )
    # Google Scholar-specific options
    parser.add_argument(
        "--delay", type=float, default=3.0,
        help="[--backend scholar] Seconds between requests (default: 3)."
    )
    parser.add_argument(
        "--use-proxy", action="store_true",
        help="[--backend scholar] Use scholarly free-proxy rotation."
    )
    parser.add_argument(
        "--scraper-api-key", default=None, metavar="KEY",
        help="[--backend scholar] ScraperAPI key for reliable proxy access."
    )
    parser.add_argument(
        "--scholar-mirror", default=None, metavar="URL",
        help="[--backend scholar] Base URL of a Google Scholar mirror site, "
             "e.g. https://scholar.example.com  (replaces scholar.google.com)."
    )
    parser.add_argument(
        "--proxy-url", default=None, metavar="URL",
        help="[--backend scholar] HTTP/HTTPS proxy URL, "
             "e.g. http://127.0.0.1:20172  (v2rayA / Clash / any local proxy)."
    )
    args = parser.parse_args()

    # ── Dependency check ──────────────────────────────────────────────────────
    if args.backend == "semantic":
        try:
            import semanticscholar  # noqa: F401
        except ImportError:
            print("ERROR: `semanticscholar` is not installed.\n  pip install semanticscholar")
            sys.exit(1)
    else:
        try:
            import scholarly  # noqa: F401
        except ImportError:
            print("ERROR: `scholarly` is not installed.\n  pip install scholarly")
            sys.exit(1)

        # Set proxy via env vars so httpx/requests picks it up automatically
        if args.proxy_url:
            import os
            os.environ["HTTP_PROXY"]  = args.proxy_url
            os.environ["HTTPS_PROXY"] = args.proxy_url
            print(f"Using proxy: {args.proxy_url}")

        # Configure mirror URL for Google Scholar backend
        if args.scholar_mirror:
            from scholarly import scholarly as sch
            sch.set_logger(False)
            # scholarly uses URLS relative to a base; override the base URL
            import scholarly._scholarly as _sch_module
            _sch_module._SCHOLARPUB_URL = args.scholar_mirror.rstrip("/") + "/scholar"
            _sch_module._SCHOLARAUTHOR_URL = args.scholar_mirror.rstrip("/") + "/citations"
            print(f"Using mirror: {args.scholar_mirror}")

        # Configure proxy for Google Scholar backend
        if args.scraper_api_key:
            from scholarly import scholarly as sch, ProxyGenerator
            pg = ProxyGenerator()
            pg.ScraperAPI(args.scraper_api_key)
            sch.use_proxy(pg)
            print("Using ScraperAPI proxy.")
        elif args.use_proxy:
            from scholarly import scholarly as sch, ProxyGenerator
            pg = ProxyGenerator()
            try:
                pg.FreeProxies()
                sch.use_proxy(pg)
                print("Using free proxy rotation.")
            except Exception as exc:
                print(f"WARNING: FreeProxies() failed ({exc}). Continuing without proxy.")
                print("  Tip: try --scraper-api-key or run on a machine with direct Scholar access.")

    members = _load_json("final_all_members.json")
    papers  = _load_json("final_all_papers.json")

    existing_titles_lower = {t.lower() for t in papers}
    new_entries = {}
    skipped = 0

    for name, info in members.items():
        # Filter by --author if specified
        if args.author and args.author.lower() not in name.lower():
            continue

        # Skip postdoctoral fellows, professor and graduated student
        degree = info.get("degree", "")
        if "postdoc" in degree.lower():
            print(f"  Skipping {name} — postdoctoral fellow")
            skipped += 1
            continue
        if "professor" in degree.lower():
            print(f"  Skipping {name} — professor")
            skipped += 1
            continue
        if "graduated" in degree.lower():
            print(f"  Skipping {name} — graduated student")
            skipped += 1
            continue

        print(f"\n[{name}]")

        # ── Fetch using selected backend ──────────────────────────────────────
        if args.backend == "semantic":
            semantic_id = info.get("semantic", "").strip()
            if not semantic_id:
                print(f"  Skipping — 'semantic' field is empty. "
                      "Fill it in final_all_members.json to enable auto-fetch.")
                skipped += 1
                continue
            pubs = _fetch_pubs_semantic(name, semantic_id, max_pubs=args.max_pubs)
            pub_to_entry = _semantic_pub_to_entry
        else:
            scholar_url = info.get("scholar", "nan")
            if not scholar_url or scholar_url == "nan":
                print(f"  Skipping — no Google Scholar URL")
                skipped += 1
                continue
            scholar_id = _extract_scholar_id(scholar_url)
            if not scholar_id:
                print(f"  Skipping — cannot parse scholar ID from: {scholar_url}")
                skipped += 1
                continue
            pubs = _fetch_pubs_scholar(scholar_id, name,
                                       fill_delay=args.delay,
                                       max_pubs=args.max_pubs)
            pub_to_entry = _scholar_pub_to_entry

        if not pubs:
            skipped += 1
            continue

        # ── Deduplicate and collect new entries ───────────────────────────────
        found_new = 0
        for pub in pubs:
            title, entry = pub_to_entry(pub, name)
            if title is None:
                continue
            if title.lower() in existing_titles_lower:
                continue
            if title.lower() in {t.lower() for t in new_entries}:
                continue
            new_entries[title] = entry
            found_new += 1
            print(f"    + NEW: [{entry[1]}] {title[:70]}{'…' if len(title) > 70 else ''}")

        if found_new == 0:
            print("    No new papers.")

        if args.backend == "scholar":
            time.sleep(args.delay)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if not new_entries:
        print("No new papers found.")
        return

    tag = "[DRY RUN] " if args.dry_run else ""
    print(f"{tag}Found {len(new_entries)} new paper(s)  ({skipped} members skipped).")

    if args.dry_run:
        print("\nNew papers (not saved):")
        for t, v in new_entries.items():
            print(f"  • [{v[1]}] {t}")
        return

    papers.update(new_entries)
    _save_json("final_all_papers.json", papers)
    print(f"Saved to final_all_papers.json  (total: {len(papers)} papers)")

    print("""
┌─ IMPORTANT: Please review the newly added papers ─────────────────────┐
│  1. Verify / correct venue names (e.g. 'NeurIPS 2024' not 'NeurIPS')  │
│  2. Fill in code / demo URLs where the value is 'nan'                  │
│  3. Assign a research tag or leave 'nan'                                │
│  4. Then regenerate the website:                                         │
│       python publications_to_html.py                                    │
└─────────────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    main()
