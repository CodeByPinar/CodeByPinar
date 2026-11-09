#!/usr/bin/env python3
"""Builds the animated, self-made profile widgets from the GitHub API (stdlib only).

  python tools/gen_stats.py          # real data (needs network; GH_TOKEN recommended)
  python tools/gen_stats.py --demo   # fake data, for design work offline

Output: assets/generated/{stats,langs,contrib,views}.svg  +  data/traffic.json (running view totals)

GitHub only keeps 14 days of repo traffic, so every run merges the API's per-day numbers into
data/traffic.json; the counter therefore keeps growing past the 14-day window.
"""
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape as esc

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "assets", "generated")
DATA = os.path.join(ROOT, "data", "traffic.json")
USER = os.environ.get("GH_USER", "CodeByPinar")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
DEMO = "--demo" in sys.argv

# ------------------------------------------------------------------ palette (same as make_assets.py)
BG, CARD, LINE = "#0e111a", "#131826", "#222a3d"
LAV, SAGE, PEACH, ROSE = "#a9b4f5", "#86d3c1", "#f1b9a1", "#e7a9c8"
TX, SUB, MU = "#ebe9f4", "#b7bdd0", "#7d869e"
SANS = "'Segoe UI Variable','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'Cascadia Code',Consolas,'SF Mono','Courier New',monospace"
LANG_COLORS = [LAV, SAGE, PEACH, ROSE, "#9ec5f4", "#d9d28f"]


# ------------------------------------------------------------------ GitHub API
def _req(url, data=None):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "profile-widgets"}
    if TOKEN:
        h["Authorization"] = "Bearer " + TOKEN
    r = urllib.request.Request(url, data=data, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30) as f:
            return json.loads(f.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        print("  ! %s -> %s" % (url.replace("https://api.github.com", ""), getattr(e, "code", e)))
        return None


def api(path):
    return _req("https://api.github.com" + path)


def graphql(query, variables):
    return _req("https://api.github.com/graphql", json.dumps({"query": query, "variables": variables}).encode())


def collect():
    d = {"stars": 0, "repos": 0, "followers": 0, "commits": 0, "prs": 0, "contrib": 0,
         "langs": {}, "days": [], "views": {}, "tracked": 0}
    u = api("/users/%s" % USER)
    if not u:
        raise SystemExit("cannot reach GitHub API (user lookup failed)")
    d["followers"], d["repos"] = u.get("followers", 0), u.get("public_repos", 0)
    repos, page = [], 1
    while True:
        chunk = api("/users/%s/repos?per_page=100&page=%d" % (USER, page)) or []
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    d["stars"] = sum(r["stargazers_count"] for r in own)
    for r in own:
        for k, v in (api("/repos/%s/%s/languages" % (USER, r["name"])) or {}).items():
            d["langs"][k] = d["langs"].get(k, 0) + v
    q = """query($login:String!){user(login:$login){contributionsCollection{totalCommitContributions
      totalPullRequestContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    g = graphql(q, {"login": USER})
    try:
        cc = g["data"]["user"]["contributionsCollection"]
        d["commits"], d["prs"] = cc["totalCommitContributions"], cc["totalPullRequestContributions"]
        d["contrib"] = cc["contributionCalendar"]["totalContributions"]
        d["days"] = [[x["date"], x["contributionCount"]] for w in cc["contributionCalendar"]["weeks"] for x in w["contributionDays"]]
    except (TypeError, KeyError):
        print("  ! no contribution calendar (token missing?) - heatmap will be empty")
    # traffic: merge into the persistent file
    store = {"days": {}}
    if os.path.exists(DATA):
        with open(DATA, encoding="utf-8") as f:
            store = json.load(f)
    for r in own:
        t = api("/repos/%s/%s/traffic/views" % (USER, r["name"]))
        if not t:
            continue
        for v in t.get("views", []):
            store["days"].setdefault(r["name"], {})[v["timestamp"][:10]] = {"c": v["count"], "u": v["uniques"]}
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=1, sort_keys=True)
    d["views"] = store["days"]
    return d


def demo():
    rnd = random.Random(7)
    today = dt.date.today()
    days = []
    for i in range(371, -1, -1):
        day = today - dt.timedelta(days=i)
        n = 0 if rnd.random() < .35 else int(rnd.random() ** 2 * 14)
        days.append([day.isoformat(), n])
    views = {"glpi-guard": {}, "glpi-surge": {}, "CodeByPinar": {}}
    for i in range(60):
        k = (today - dt.timedelta(days=i)).isoformat()
        for r, m in (("glpi-guard", 40), ("glpi-surge", 25), ("CodeByPinar", 15)):
            views[r][k] = {"c": int(rnd.random() * m) + 2, "u": int(rnd.random() * m / 3) + 1}
    return {"stars": 128, "repos": 14, "followers": 63, "commits": 842, "prs": 37, "contrib": sum(x[1] for x in days),
            "langs": {"PHP": 612000, "Python": 180000, "JavaScript": 96000, "Twig": 54000, "Shell": 21000, "CSS": 12000},
            "days": days, "views": views, "tracked": 3}


# ------------------------------------------------------------------ svg helpers
def svg(name, w, h, body, defs=""):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{name}">'
         f'<defs>{defs}<filter id="b2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>'
         f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{LAV}"/><stop offset=".5" stop-color="{ROSE}"/><stop offset="1" stop-color="{PEACH}"/></linearGradient>'
         f'<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#171d2e"/><stop offset="1" stop-color="{CARD}"/></linearGradient>'
         f'<clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>{body}</svg>')
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(s)


def T(x, y, s, size=15, fill=TX, font=SANS, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{esc(str(s))}</text>')


def panel(w, h, r=24):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#card)"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{LINE}"/>')


def aura(cx, cy, r, c, op):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{op}" filter="url(#b2)"/>'


def fmt(n):
    return f"{int(n):,}".replace(",", ".") if n < 1e7 else f"{n / 1e6:.1f}M"


def countup(x, y, value, size, fill, t0, anchor="start", weight=650, font=SANS):
    """Number that counts up (eased, 18 frames) using only SMIL <set> - works inside <img>."""
    if value <= 0:
        return T(x, y, 0, size, fill, font, weight, anchor)
    n, step, out = 18, .045, ""
    for k in range(n):
        v = round(value * (1 - (1 - k / (n - 1)) ** 3))
        on = t0 + k * step
        o = T(x, y, fmt(v), size, fill, font, weight, anchor, 'opacity="0"')
        sets = f'<set attributeName="opacity" to="1" begin="{on:.3f}s" fill="freeze"/>'
        if k < n - 1:
            sets += f'<set attributeName="opacity" to="0" begin="{on + step:.3f}s" fill="freeze"/>'
        out += o.replace("</text>", sets + "</text>")
    return out


def rise(inner, x, y, t0, dist=14):
    return (f'<g transform="translate({x} {y})"><g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t0}s" dur=".8s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 {dist}" to="0 0" begin="{t0}s" dur=".8s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>'
            f'{inner}</g></g>')


def stamp(y=28):
    return T(1176, y, "updated " + dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), 11, MU, MONO, anchor="end")


ICONS = {
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9 6.8 19.7l1-5.9L3.5 9.7l5.9-.8z"/>',
    "repo": '<path d="M5 4.5h11a2 2 0 0 1 2 2V19H7a2 2 0 0 1-2-2zM5 17a2 2 0 0 1 2-2h11M9 8h5"/>',
    "users": '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19c.4-3.3 2.7-5 5.5-5s5.1 1.7 5.5 5M16 6.2a3 3 0 0 1 0 5.6M18.5 14.6c1.4.8 2.2 2.2 2.5 4.4"/>',
    "commit": '<circle cx="12" cy="12" r="3.6"/><path d="M3 12h5.4M15.6 12H21"/>',
    "pr": '<circle cx="6.5" cy="6" r="2.2"/><circle cx="6.5" cy="18" r="2.2"/><circle cx="17.5" cy="18" r="2.2"/><path d="M6.5 8.2v7.6M17.5 15.8V10a3 3 0 0 0-3-3H11M13 4.5L10.5 7 13 9.5"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.6 2.6M15.4 15.4L18 18M18 6l-2.6 2.6M8.6 15.4L6 18"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
}


def icon(kind, c, size=22):
    return (f'<g transform="scale({size / 24})" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[kind]}</g>')


# ------------------------------------------------------------------ widgets
def w_stats(d):
    tiles = [("Stars", d["stars"], "star", PEACH), ("Repositories", d["repos"], "repo", LAV),
             ("Followers", d["followers"], "users", SAGE), ("Commits · 12 mo", d["commits"], "commit", ROSE),
             ("Pull requests", d["prs"], "pr", LAV), ("Contributions", d["contrib"], "spark", SAGE)]
    w, h, gap = 1200, 156, 14
    tw = (w - gap * 5) / 6
    body, defs = "", ""
    for i, (lab, val, ic, c) in enumerate(tiles):
        x, t0 = i * (tw + gap), .2 + i * .18
        defs += f'<clipPath id="t{i}"><rect width="{tw}" height="{h}" rx="22"/></clipPath>'
        inner = (f'<g clip-path="url(#t{i})"><rect width="{tw}" height="{h}" fill="url(#card)"/>{aura(tw - 20, 10, 60, c, .26)}</g>'
                 f'<rect x=".5" y=".5" width="{tw - 1}" height="{h - 1}" rx="21.5" fill="none" stroke="{LINE}"/>'
                 f'<circle cx="38" cy="40" r="19" fill="{c}" fill-opacity=".13"/><g transform="translate(27 29)">{icon(ic, c)}</g>'
                 + T(24, 98, lab, 13, MU, SANS, 500) + countup(24, 132, val, 34, TX, t0 + .3))
        body += rise(inner, x, 0, t0)
    svg("stats", w, h, body, defs)


def w_langs(d):
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    tot = sum(v for _, v in langs) or 1
    w, rh = 1200, 62
    rows = (len(langs) + 1) // 2
    h = 36 + rows * rh + 40
    body = panel(w, h) + T(36, 40, "Most used languages", 15, SUB, SANS, 600) + stamp()
    # stacked overview bar
    x = 36
    for i, (k, v) in enumerate(langs):
        sw = (w - 72) * v / tot
        c = LANG_COLORS[i % 6]
        body += (f'<rect x="{x:.1f}" y="58" width="0" height="10" fill="{c}"><animate attributeName="width" from="0" to="{max(sw - 3, 1):.1f}" begin="{.3 + i * .12}s" dur=".9s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')
        x += sw
    body = body.replace('<rect x="36.0" y="58"', '<rect x="36.0" y="58" rx="5"', 1)
    for i, (k, v) in enumerate(langs):
        c, col, row = LANG_COLORS[i % 6], i % 2, i // 2
        x0, y0 = 36 + col * 580, 100 + row * rh
        pct = v * 100 / tot
        bw = 520 * pct / 100
        t0 = .6 + i * .15
        body += (f'<circle cx="{x0 + 5}" cy="{y0 - 5}" r="5" fill="{c}"/>' + T(x0 + 20, y0, k, 15.5, TX, SANS, 600)
                 + T(x0 + 520, y0, f"{pct:.1f}%", 13, MU, MONO, anchor="end")
                 + f'<rect x="{x0}" y="{y0 + 12}" width="520" height="6" rx="3" fill="{LINE}"/>'
                 + f'<rect x="{x0}" y="{y0 + 12}" width="0" height="6" rx="3" fill="{c}"><animate attributeName="width" from="0" to="{max(bw, 4):.1f}" begin="{t0}s" dur="1.1s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')
    svg("langs", w, h, body)


def w_contrib(d):
    days = d["days"]
    w, pitch, cell = 1200, 21, 17
    h = 252
    body = panel(w, h) + T(40, 44, f"{fmt(d['contrib'])} contributions in the last year", 17, TX, SANS, 600)
    if not days:
        svg("contrib", w, h, body + T(w // 2, 140, "no contribution data (token needed)", 14, MU, MONO, anchor="middle"))
        return
    vals = sorted(v for _, v in days if v)
    q = [vals[int(len(vals) * p)] for p in (.25, .5, .75)] if vals else [1, 2, 3]
    shades = ["#1a2133", "#34406f", "#5967b4", "#8795e6", "#c3cbfb"]

    def lvl(n):
        return 0 if n == 0 else 1 + sum(n > t for t in q)

    first = dt.date.fromisoformat(days[0][0])
    off = (first.weekday() + 1) % 7  # weeks start on Sunday
    gx, gy = 40, 78
    cells, months, last_m = "", "", None
    for i, (ds, n) in enumerate(days):
        dd = dt.date.fromisoformat(ds)
        col, row = (i + off) // 7, (i + off) % 7
        x, y = gx + col * pitch, gy + row * pitch
        if row == 0 and dd.month != last_m and col < 51:
            months += T(x, 66, dd.strftime("%b"), 11.5, MU, MONO)
            last_m = dd.month
        L = lvl(n)
        if L == 0:
            cells += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="5" fill="{shades[0]}"/>'
        else:
            cells += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="5" fill="{shades[L]}" opacity="0">'
                      f'<animate attributeName="opacity" from="0" to="1" begin="{.2 + col * .028 + row * .02:.3f}s" dur=".5s" fill="freeze"/></rect>')
    last = len(days) - 1
    col, row = (last + off) // 7, (last + off) % 7
    px, py = gx + col * pitch + cell / 2, gy + row * pitch + cell / 2
    pulse = (f'<circle cx="{px}" cy="{py}" r="{cell / 2}" fill="none" stroke="{PEACH}" stroke-width="1.5" opacity="0">'
             f'<animate attributeName="r" values="{cell / 2};{cell * 1.4}" dur="2.4s" begin="2.2s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values=".9;0" dur="2.4s" begin="2.2s" repeatCount="indefinite"/></circle>')
    gw = (col + 1) * pitch
    sweep = (f'<g clip-path="url(#gridclip)"><rect x="{gx - 140}" y="{gy - 6}" width="140" height="{7 * pitch + 12}" fill="url(#sw)" opacity=".55">'
             f'<animate attributeName="x" from="{gx - 140}" to="{gx + gw}" dur="7s" begin="3s;sweep.end+4s" id="sweep"/></rect></g>')
    defs = (f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="gridclip"><rect x="{gx}" y="{gy - 6}" width="{gw}" height="{7 * pitch + 12}"/></clipPath>')
    legend = T(w - 40 - 5 * 22 - 44, 44, "Less", 11.5, MU, MONO, anchor="end") + "".join(
        f'<rect x="{w - 40 - 5 * 22 - 34 + i * 22}" y="33" width="14" height="14" rx="4" fill="{s}"/>' for i, s in enumerate(shades)) + T(w - 40 - 6, 44, "More", 11.5, MU, MONO)
    svg("contrib", w, h, body + months + cells + sweep + pulse + legend + stamp(h - 16), defs)


def smooth(pts):
    p = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx = (x0 + x1) / 2
        p += f" C{mx:.1f} {y0:.1f} {mx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}"
    return p


def w_views(d):
    today = dt.date.today()
    per_day = {}
    total_c = total_u = 0
    first = None
    for repo, ds in d["views"].items():
        for k, v in ds.items():
            per_day[k] = per_day.get(k, 0) + v["c"]
            total_c += v["c"]
            total_u += v["u"]
            first = k if first is None or k < first else first
    series = [per_day.get((today - dt.timedelta(days=i)).isoformat(), 0) for i in range(29, -1, -1)]
    last14 = sum(series[-14:])
    best = max(series) if series else 0
    w, h = 1200, 228
    sx, sy, sw, sh = 720, 78, 430, 104
    mx = max(max(series), 1)
    pts = [(sx + i * sw / (len(series) - 1), sy + sh - (v / mx) * sh * .92 - 4) for i, v in enumerate(series)]
    line = smooth(pts)
    area = line + f" L{sx + sw} {sy + sh} L{sx} {sy + sh} Z"
    body = (f'<g clip-path="url(#c)">{panel(w, h)}{aura(150, 30, 120, LAV, .24)}{aura(1080, 200, 130, ROSE, .20)}</g>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{LINE}"/>' + stamp())
    # left: headline counter
    body += (f'<circle cx="62" cy="62" r="21" fill="{LAV}" fill-opacity=".14"/><g transform="translate(50 50)">{icon("eye", LAV, 24)}</g>'
             + T(96, 68, "Repository views", 16, SUB, SANS, 600)
             + countup(40, 150, total_c, 64, TX, .4)
             + T(42, 186, ("since " + first + " · " if first else "") + f"{fmt(total_u)} unique visitors", 13.5, MU, SANS))
    # middle metrics
    for i, (lab, v, c) in enumerate([("Last 14 days", last14, SAGE), ("Best day", best, PEACH), ("Repos tracked", len(d["views"]) or d["tracked"], ROSE)]):
        x, y = 400, 62 + i * 52
        body += rise(f'<circle cx="0" cy="-5" r="4" fill="{c}"/>' + T(16, 0, lab, 13, MU, SANS, 500) + countup(16, 28, v, 24, TX, 1.0 + i * .2 + .3, weight=650), x, y, 1.0 + i * .2, 10)
    # right: sparkline
    body += T(sx, 58, "last 30 days", 12, MU, MONO)
    for i in range(4):
        gy = sy + i * sh / 3
        body += f'<path d="M{sx} {gy:.1f}H{sx + sw}" stroke="{LINE}" stroke-dasharray="2 6"/>'
    defs = (f'<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LAV}" stop-opacity=".38"/><stop offset="1" stop-color="{LAV}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{SAGE}"/><stop offset=".5" stop-color="{LAV}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient>')
    ex, ey = pts[-1]
    body += (f'<path d="{area}" fill="url(#ar)" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.4s" dur="1.2s" fill="freeze"/></path>'
             f'<path d="{line}" pathLength="1" fill="none" stroke="url(#ln)" stroke-width="3" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1">'
             f'<animate attributeName="stroke-dashoffset" from="1" to="0" begin=".6s" dur="1.8s" fill="freeze" calcMode="spline" keySplines=".4 0 .2 1" keyTimes="0;1"/></path>'
             f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{ROSE}" opacity="0"><set attributeName="opacity" to="1" begin="2.3s" fill="freeze"/></circle>'
             f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="none" stroke="{ROSE}" stroke-width="2" opacity="0">'
             f'<animate attributeName="r" values="5;16" dur="2.2s" begin="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.2s" begin="2.4s" repeatCount="indefinite"/></circle>')
    svg("views", w, h, body, defs)


def main():
    d = demo() if DEMO else collect()
    for fn in (w_stats, w_langs, w_contrib, w_views):
        fn(d)
    print("widgets ->", OUT, "(demo)" if DEMO else "")


if __name__ == "__main__":
    main()
