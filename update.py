#!/usr/bin/env python3
"""
Cursor Watch — daily tracker pipeline.

Pulls fresh signal on Cursor (Anysphere) via Firecrawl (scrape + search),
merges it with a verified seed of facts, and regenerates:
  - docs/data.json        (machine-readable snapshot)
  - docs/index.html       (the live dashboard, with PDF export)
  - digests/YYYY-MM-DD.md (dated newsletter digest)
  - latest-digest.md      (most recent digest, for the newsletter merge)

Only dependency: requests. Only secret: FIRECRAWL_API_KEY.
"""
import os, re, json, html, datetime, pathlib, sys
import requests

ROOT = pathlib.Path(__file__).parent
DOCS = ROOT / "docs"
DIGESTS = ROOT / "digests"
DOCS.mkdir(exist_ok=True)
DIGESTS.mkdir(exist_ok=True)

KEY = os.environ.get("FIRECRAWL_API_KEY", "").strip()
if not KEY:
    kf = ROOT / ".firecrawl_key"
    if kf.exists():
        KEY = kf.read_text().strip()
if not KEY:
    print("ERROR: FIRECRAWL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

FC = "https://api.firecrawl.dev/v1"
HEAD = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
TODAY = datetime.date.today().isoformat()


def fc_scrape(url):
    try:
        r = requests.post(f"{FC}/scrape", headers=HEAD, timeout=70,
                          json={"url": url, "formats": ["markdown"], "onlyMainContent": True})
        if r.status_code == 200:
            return r.json().get("data", {}).get("markdown", "") or ""
    except Exception as e:
        print(f"scrape fail {url}: {e}", file=sys.stderr)
    return ""


def fc_search(query, limit=6):
    try:
        r = requests.post(f"{FC}/search", headers=HEAD, timeout=70,
                          json={"query": query, "limit": limit})
        if r.status_code == 200:
            data = r.json().get("data", [])
            if isinstance(data, dict):
                data = data.get("web") or data.get("results") or []
            out = []
            for x in data:
                u = x.get("url"); t = x.get("title")
                if u and t:
                    out.append({"title": t.strip(), "url": u.strip()})
            return out
    except Exception as e:
        print(f"search fail '{query}': {e}", file=sys.stderr)
    return []


def domain(u):
    m = re.search(r"https?://([^/]+)/?", u or "")
    return m.group(1).replace("www.", "") if m else ""


def parse_changelog(md):
    """Extract changelog entries: optional version + 'Mon DD, YYYY' + url, then a summary."""
    entries = []
    pat = re.compile(r"\[(\d+\.\d+)?([A-Z][a-z]{2,8}\.?\s+\d{1,2},\s+\d{4})\]\((https://cursor\.com/changelog/[^)]+)\)")
    for m in pat.finditer(md):
        ver, date, url = m.group(1), m.group(2), m.group(3)
        tail = md[m.end():m.end() + 800]
        tail = re.sub(r"^\s*·\s*\[[^\]]*\]\([^)]*\)", "", tail)  # drop "· [Changelog](...)"
        summ = ""
        for line in tail.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("[") or line.startswith("!"):
                continue
            line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)  # link -> text
            line = re.sub(r"[*`\\]", "", line)
            if len(line) > 40:
                summ = re.sub(r"\s+", " ", line)[:240]
                break
        entries.append({"version": ver or "—", "date": date, "url": url, "summary": summ})
        if len(entries) >= 8:
            break
    seen, uniq = set(), []
    for e in entries:
        k = e["version"] + e["date"]
        if k in seen:
            continue
        seen.add(k); uniq.append(e)
    return uniq


def yt_id(u):
    m = re.search(r"(?:v=|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})", u or "")
    return m.group(1) if m else None


# Domains we don't want in the article feeds (videos have their own panel;
# these others are low-signal or known SEO-spam).
JUNK = ("pinterest.", "facebook.", "tiktok.", "youtube.", "youtu.be",
        "instagram.", "tech-insider.org", "m.youtube.")


def collect():
    seed = json.loads((ROOT / "seed.json").read_text())

    # --- product velocity: live changelog ---
    changelog = parse_changelog(fc_scrape("https://cursor.com/changelog"))

    # --- fresh news (funding / market / strategic) ---
    news = []
    for q in ["Cursor Anysphere funding valuation news",
              "Cursor Anysphere AI coding news 2026",
              "SpaceX xAI Cursor acquisition"]:
        news += fc_search(q, 6)

    # --- company adoption signals ---
    adoption = []
    for q in ["company adopts Cursor AI editor engineers",
              "enterprise standardizes on Cursor developers",
              "jobs require Cursor AI coding experience"]:
        adoption += fc_search(q, 6)

    # --- videos: short build tutorials ---
    vids = fc_search("Cursor build app tutorial youtube", 8) + \
           fc_search("Cursor AI workflow demo build youtube", 6)
    videos = list(seed.get("videos", []))
    have = {v["id"] for v in videos}
    for v in vids:
        i = yt_id(v["url"])
        if i and i not in have:
            videos.append({"title": v["title"], "id": i, "note": ""})
            have.add(i)
    videos = videos[:6]

    def clean(items):
        seen, out = set(), []
        for x in items:
            u = x["url"]; d = domain(u)
            if u in seen or any(j in d for j in JUNK):
                continue
            seen.add(u)
            out.append({"title": x["title"], "url": u, "source": d, "seen": TODAY})
        return out[:12]

    data = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "as_of": TODAY,
        "company": seed["company"],
        "funding_timeline": seed["funding_timeline"],
        "adopters": seed["adopters"],
        "product_milestones": seed["product_milestones"],
        "changelog": changelog,
        "news": clean(news),
        "adoption_signals": clean(adoption),
        "videos": videos,
    }
    return data


# ----------------------------- rendering --------------------------------------
def esc(s):
    return html.escape(str(s or ""))


def render_dashboard(d):
    payload = json.dumps(d).replace("</", "<\\/")
    tpl = (DOCS / "_template.html")
    base = TEMPLATE
    return base.replace("/*DATA*/null/*DATA*/", payload)


def render_digest(d):
    c = d["company"]
    lines = []
    lines.append(f"## 🖱️ Cursor Watch — {d['as_of']}")
    lines.append("")
    lines.append(f"**Where it stands:** {c['latest_valuation']}. {c['latest_arr']}. {c['fortune500']}.")
    lines.append("")
    lines.append(f"**Headline:** {c['headline_deal']}")
    lines.append("")
    if d["changelog"]:
        cl = d["changelog"][0]
        lines.append(f"**Shipped (latest, v{cl['version']} · {cl['date']}):** {cl['summary']}")
        lines.append("")
    if d["adoption_signals"]:
        lines.append("**Adoption signals today:**")
        for s in d["adoption_signals"][:3]:
            lines.append(f"- [{s['title']}]({s['url']}) — _{s['source']}_")
        lines.append("")
    if d["news"]:
        lines.append("**In the news:**")
        for s in d["news"][:3]:
            lines.append(f"- [{s['title']}]({s['url']}) — _{s['source']}_")
        lines.append("")
    if d["videos"]:
        v = d["videos"][0]
        lines.append(f"**▶️ Watch it built:** [{v['title']}](https://www.youtube.com/watch?v={v['id']})")
        lines.append("")
    lines.append(f"🔗 **Full live dashboard:** {DASHBOARD_URL}")
    lines.append("")
    lines.append("_Auto-generated daily via Firecrawl. Figures from press reports; verify before relying on them._")
    return "\n".join(lines)


DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://eferrao.github.io/cursor-watch/")

# Dashboard template is imported from template.py to keep this file readable.
from template import TEMPLATE


def main():
    d = collect()
    (DOCS / "data.json").write_text(json.dumps(d, indent=2))
    (DOCS / "index.html").write_text(render_dashboard(d))
    digest = render_digest(d)
    (DIGESTS / f"{TODAY}.md").write_text(digest)
    (ROOT / "latest-digest.md").write_text(digest)
    print(f"OK — {len(d['changelog'])} changelog, {len(d['news'])} news, "
          f"{len(d['adoption_signals'])} adoption, {len(d['videos'])} videos")


if __name__ == "__main__":
    main()
