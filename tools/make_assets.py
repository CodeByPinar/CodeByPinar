#!/usr/bin/env python3
"""Calm 'aura' profile graphics, hand-written SVG (no third-party image services).
Run:  python tools/make_assets.py   ->  assets/*.svg
"""
import os
from xml.sax.saxutils import escape as esc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG, CARD, LINE = "#0e111a", "#131826", "#222a3d"
LAV, SAGE, PEACH, ROSE = "#a9b4f5", "#86d3c1", "#f1b9a1", "#e7a9c8"
TX, SUB, MU = "#ebe9f4", "#b7bdd0", "#7d869e"
SANS = "'Segoe UI Variable','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'Cascadia Code',Consolas,'SF Mono','Courier New',monospace"


def save(name, w, h, body, defs=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(name)}">'
           f'<defs>{defs}<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="46"/></filter>'
           f'<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>'
           f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{LAV}"/><stop offset=".5" stop-color="{ROSE}"/>'
           f'<stop offset="1" stop-color="{PEACH}"/></linearGradient>'
           f'<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#171d2e"/><stop offset="1" stop-color="{CARD}"/></linearGradient>'
           f'<clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath></defs>{body}</svg>')
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def T(x, y, s, size=15, fill=TX, font=SANS, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def panel(w, h, r=24):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#card)"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{LINE}"/>')


def aura(cx, cy, r, c, op=.35, blur="blur", drift=0):
    mv = (f'<animateTransform attributeName="transform" type="translate" values="0 0;{drift} {-drift * .6};0 0" dur="14s" repeatCount="indefinite"/>'
          if drift else "")
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="{op}" filter="url(#{blur})">{mv}</circle>'


def banner():
    w, h = 1200, 340
    rings = "".join(f'<circle cx="940" cy="170" r="{r}" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.2"/>'
                    for r, c, o in [(150, LAV, .28), (112, ROSE, .30), (76, PEACH, .34)])
    pills, x = "", 80
    for t, c in [("GLPI plugins", LAV), ("IT risk automation", SAGE), ("Open source", PEACH)]:
        pw = 34 + len(t) * 8.4
        pills += (f'<rect x="{x}" y="258" width="{pw}" height="34" rx="17" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-opacity=".38"/>'
                  f'<circle cx="{x + 18}" cy="275" r="3.5" fill="{c}"/>' + T(x + 30, 280, t, 14, TX, weight=500))
        x += pw + 12
    body = f'''<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{BG}"/>
{aura(180, 40, 190, LAV, .26, drift=30)}{aura(760, 330, 200, ROSE, .20, drift=-26)}{aura(1010, 70, 210, SAGE, .20, drift=24)}{aura(1120, 300, 150, PEACH, .18)}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
{T(80, 96, "hello, I'm", 17, MU, MONO)}
{T(78, 170, "Pınar Topuz", 66, TX, SANS, 600, extra='letter-spacing="-1"')}
<rect x="82" y="192" width="64" height="3" rx="1.5" fill="url(#g)"/>
{T(80, 226, "Software developer · GLPI plugins & IT risk automation", 19, SUB)}
{pills}
{rings}<circle cx="940" cy="170" r="40" fill="url(#g)" opacity=".85"/><circle cx="940" cy="170" r="40" fill="none" stroke="#fff" stroke-opacity=".25"/>
<circle cx="1062" cy="96" r="5" fill="{SAGE}"/><circle cx="822" cy="236" r="4" fill="{LAV}"/><circle cx="1040" cy="262" r="3.5" fill="{PEACH}"/>'''
    save("banner", w, h, body)


def heading(slug, label, color):
    w, h = 1200, 44
    lw = 44 + len(label) * 11.5
    body = (f'<circle cx="10" cy="22" r="5" fill="{color}"/><circle cx="10" cy="22" r="10" fill="{color}" opacity=".18"/>'
            + T(32, 29, label, 22, TX, SANS, 600)
            + f'<path d="M{lw} 22H{w}" stroke="{LINE}" stroke-width="1.5"/>'
            + f'<path d="M{lw} 22H{lw + 90}" stroke="{color}" stroke-opacity=".7" stroke-width="1.5"/>')
    save("h-" + slug, w, h, body)


def icon(kind, c):
    s = f'fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    return {
        "github": f'<path {s} d="M12 3a9 9 0 0 0-2.8 17.5c.45.1.6-.2.6-.43v-1.6c-2.5.55-3-1.2-3-1.2-.4-1-1-1.3-1-1.3-.8-.55.1-.55.1-.55.9.07 1.4.95 1.4.95.8 1.4 2.1 1 2.6.77.1-.6.3-1 .57-1.2-2-.23-4.1-1-4.1-4.4 0-1 .35-1.8.93-2.4-.1-.23-.4-1.15.1-2.4 0 0 .75-.25 2.5.93a8.6 8.6 0 0 1 4.6 0c1.7-1.18 2.5-.93 2.5-.93.5 1.25.2 2.17.1 2.4.6.6.93 1.4.93 2.4 0 3.4-2.1 4.2-4.1 4.4.3.27.6.8.6 1.6v2.4c0 .23.15.53.6.43A9 9 0 0 0 12 3z"/>',
        "linkedin": f'<g {s}><rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M8 10.5V16M8 7.8v.1M12 16v-5.5M12 13c0-1.6 1-2.5 2.3-2.5S16.5 11.4 16.5 13V16"/></g>',
        "mail": f'<g {s}><rect x="3" y="5.5" width="18" height="13" rx="3"/><path d="M3.5 7.5l8.5 6 8.5-6"/></g>',
        "x": f'<g {s}><path d="M5 4.5l14 15M19 4.5L5 19.5"/></g>',
        "insta": f'<g {s}><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r=".6"/></g>',
    }[kind]


def button(slug, label, sub, kind, color):
    w, h = 232, 56
    body = f'''<rect width="{w}" height="{h}" rx="28" fill="url(#card)"/>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{color}" stroke-opacity=".40"/>
<circle cx="32" cy="28" r="17" fill="{color}" fill-opacity=".14"/>
<g transform="translate(20 16)">{icon(kind, color)}</g>
{T(62, 25, label, 15.5, TX, SANS, 600)}{T(62, 43, sub, 12, MU, SANS)}'''
    save("btn-" + slug, w, h, body)


def card(slug, title, tag, desc, chips, accent):
    w, h = 380, 224
    rows = "".join(T(28, 108 + i * 22, d, 14, SUB) for i, d in enumerate(desc))
    cx, chip = 28, ""
    for c in chips:
        pw = 26 + len(c) * 7.6
        chip += (f'<rect x="{cx}" y="178" width="{pw}" height="26" rx="13" fill="{accent}" fill-opacity=".10" stroke="{accent}" stroke-opacity=".35"/>'
                 + T(cx + pw / 2, 195.5, c, 12, accent, MONO, anchor="middle"))
        cx += pw + 8
    body = f'''<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#card)"/>{aura(w - 30, 20, 90, accent, .30, "blur2")}</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
<circle cx="34" cy="42" r="4.5" fill="{accent}"/>{T(48, 47, tag, 11.5, accent, MONO, 600, extra='letter-spacing="1.6"')}
{T(28, 86, title, 27, TX, SANS, 650)}{rows}{chip}'''
    save("card-" + slug, w, h, body)


def stack():
    groups = [("Backend", LAV, ["PHP", "Twig", "Python", "JavaScript", "SQL"]),
              ("Platform", SAGE, ["GLPI 10 / 11 / 12", "Plugin API", "MySQL", "MariaDB", "REST"]),
              ("Security", ROSE, ["IT risk", "InfoSec", "Hardening", "Audit", "SPK BSY"]),
              ("Delivery", PEACH, ["Linux", "Git", "GitHub Actions", "Docker", "SSH"])]
    w, row = 1200, 68
    h = 32 + row * len(groups)
    body = panel(w, h)
    for gi, (name, col, items) in enumerate(groups):
        y = 30 + gi * row
        if gi:
            body += f'<path d="M36 {y - 6}H{w - 36}" stroke="{LINE}" stroke-opacity=".7"/>'
        body += f'<circle cx="46" cy="{y + 24}" r="4" fill="{col}"/>' + T(62, y + 29, name, 15, col, SANS, 600)
        x = 200
        for it in items:
            pw = 34 + len(it) * 8.9
            body += (f'<rect x="{x}" y="{y + 6}" width="{pw}" height="36" rx="18" fill="{col}" fill-opacity=".09" stroke="{col}" stroke-opacity=".30"/>'
                     + T(x + pw / 2, y + 29, it, 14.5, TX, SANS, 500, "middle"))
            x += pw + 12
    save("stack", w, h, body)


def certs():
    items = [("Networking Basics", "Cisco Networking Academy", "Jun 2026", SAGE),
             ("Cyber Threat Management", "Cisco Networking Academy", "May 2026", LAV),
             ("Getting Started with Packet Tracer", "Cisco Networking Academy", "May 2026", ROSE),
             ("Penetration Testing (Ethical Hacking)", "AltaySec Akademi", "Mar 2026", PEACH),
             ("Introduction to Cybersecurity", "Cisco Networking Academy", "Aug 2025", SAGE)]
    w, row = 1200, 64
    h = 40 + row * len(items)
    body = panel(w, h) + f'<path d="M52 56V{h - 52}" stroke="{LINE}" stroke-width="2"/>'
    for i, (t, p, d, c) in enumerate(items):
        y = 28 + i * row
        body += (f'<circle cx="52" cy="{y + 28}" r="7" fill="{CARD}" stroke="{c}" stroke-width="2.5"/>'
                 + T(84, y + 26, t, 18, TX, SANS, 600) + T(84, y + 47, p, 13, MU)
                 + f'<rect x="{w - 164}" y="{y + 12}" width="128" height="32" rx="16" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-opacity=".35"/>'
                 + T(w - 100, y + 33, d, 13.5, c, MONO, anchor="middle"))
    save("certs", w, h, body)


def focus():
    items = [("GLPI plugins", "Risk, compliance and audit workflows that configure from the UI.", LAV),
             ("Defensive tooling", "Read-only scanners and hardening checks with clear remediation.", SAGE),
             ("Open source", "Surge, glpi-guard and create-glpi-plugin, documented and tested.", PEACH),
             ("Security labs", "SIEM, incident response and network defense practice.", ROSE)]
    cw, ch, gap = 592, 118, 16
    w, h = 1200, 2 * ch + gap
    body = ""
    for i, (t, d, c) in enumerate(items):
        x, y = (i % 2) * (cw + gap), (i // 2) * (ch + gap)
        body += (f'<g transform="translate({x} {y})"><g clip-path="url(#c{i})"><rect width="{cw}" height="{ch}" fill="url(#card)"/>{aura(cw - 10, 10, 70, c, .28, "blur2")}</g>'
                 f'<rect x=".5" y=".5" width="{cw - 1}" height="{ch - 1}" rx="21.5" fill="none" stroke="{LINE}"/>'
                 f'<circle cx="46" cy="42" r="5" fill="{c}"/><circle cx="46" cy="42" r="12" fill="{c}" opacity=".16"/>'
                 + T(70, 49, t, 21, TX, SANS, 600) + T(34, 84, d, 14.5, SUB) + '</g>')
    defs = "".join(f'<clipPath id="c{i}"><rect width="{cw}" height="{ch}" rx="22"/></clipPath>' for i in range(4))
    save("focus", w, h, body, defs)


def footer():
    w, h = 1200, 150
    body = f'''<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#card)"/>
{aura(250, 150, 150, LAV, .30, "blur2")}{aura(620, 170, 160, ROSE, .24, "blur2")}{aura(980, 150, 150, PEACH, .26, "blur2")}</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
{T(w // 2, 70, "Secure systems are designed, never accidental.", 26, TX, SANS, 500, "middle")}
{T(w // 2, 104, "build · defend · document · ship", 14, MU, MONO, anchor="middle", extra='letter-spacing="2"')}'''
    save("footer", w, h, body)


def divider():
    save("divider", 1200, 24, f'<path d="M0 12H1200" stroke="{LINE}" stroke-width="1.5"/><circle cx="600" cy="12" r="5" fill="url(#g)"/>')


def about():
    w, h = 1200, 330
    chips, x = "", 330
    for t, c in [("Samsun, Türkiye · remote", LAV), ("Freelance since Jun 2026", SAGE), ("GLPI 10 / 11 / 12", PEACH), ("TR · EN", ROSE)]:
        pw = 36 + len(t) * 8.2
        chips += (f'<rect x="{x}" y="262" width="{pw}" height="34" rx="17" fill="{c}" fill-opacity=".09" stroke="{c}" stroke-opacity=".38"/>'
                  f'<circle cx="{x + 18}" cy="279" r="3.5" fill="{c}"/>' + T(x + 30, 284, t, 13.5, TX, weight=500))
        x += pw + 10
    orb = "".join(f'<circle cx="150" cy="150" r="{r}" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="1.2"/>'
                  for r, c, o in [(112, LAV, .30), (88, ROSE, .32), (64, PEACH, .36)])
    body = f"""<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#card)"/>
{aura(150, 150, 120, LAV, .30, "blur2")}{aura(1090, 40, 150, SAGE, .16, "blur2")}{aura(900, 330, 170, ROSE, .14, "blur2")}</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
{orb}<circle cx="150" cy="150" r="46" fill="url(#g)" opacity=".92"/><circle cx="150" cy="150" r="46" fill="none" stroke="#fff" stroke-opacity=".28"/>
{T(150, 166, "P", 46, BG, SANS, 700, "middle")}
<circle cx="262" cy="92" r="4" fill="{SAGE}"/><circle cx="58" cy="228" r="3.5" fill="{PEACH}"/><circle cx="232" cy="236" r="3" fill="{LAV}"/>
{T(330, 62, "about me", 14, MU, MONO, extra='letter-spacing="2"')}
{T(330, 112, "I turn compliance into software", 38, TX, SANS, 650, extra='letter-spacing="-.5"')}
<rect x="332" y="128" width="56" height="3" rx="1.5" fill="url(#g)"/>
{T(330, 170, "Hi, I'm Pınar, a freelance GLPI plugin & IT risk automation developer.", 17.5, SUB)}
{T(330, 198, "I take information-security requirements and make them configurable from the UI,", 17.5, SUB)}
{T(330, 226, "portable and auto-calculating: risk scoring, approval flows, audits, reports.", 17.5, SUB)}
{chips}"""
    save("about", w, h, body)


def principles():
    items = [("Attacker-aware", "I design with the attacker's view in mind: least privilege, no secrets in output, nothing magic in production.", LAV, "shield"),
             ("Read-only by default", "Scanners and reports look, never touch. Writes are explicit, backed up and reversible.", SAGE, "eye"),
             ("Documented & tested", "Every plugin ships with tests, TR/EN docs and a changelog, so it survives its author.", PEACH, "check")]
    gl = {"shield": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 7.8-7.5 9.5-4.3-1.7-7.5-5-7.5-9.5V6z"/><path d="M8.8 12l2.2 2.2 4.2-4.4"/>',
          "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
          "check": '<rect x="4" y="4" width="16" height="16" rx="4"/><path d="M8.5 12.3l2.5 2.5 4.6-5"/>'}
    w, h, gap = 1200, 190, 16
    cw = (w - 2 * gap) / 3
    body, defs = "", ""
    for i, (t, d, c, g) in enumerate(items):
        x = i * (cw + gap)
        defs += f'<clipPath id="p{i}"><rect width="{cw}" height="{h}" rx="22"/></clipPath>'
        lines, cur = [], ""
        for wd in d.split():
            if len(cur) + len(wd) > 50:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        txt = "".join(T(28, 112 + j * 22, ln, 14, SUB) for j, ln in enumerate(lines))
        body += (f'<g transform="translate({x} 0)"><g clip-path="url(#p{i})"><rect width="{cw}" height="{h}" fill="url(#card)"/>{aura(cw - 20, 10, 80, c, .26, "blur2")}</g>'
                 f'<rect x=".5" y=".5" width="{cw - 1}" height="{h - 1}" rx="21.5" fill="none" stroke="{LINE}"/>'
                 f'<circle cx="52" cy="48" r="22" fill="{c}" fill-opacity=".13"/><g transform="translate(40 36)" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{gl[g]}</g>'
                 + T(88, 55, t, 20, TX, SANS, 600) + txt + '</g>')
    save("principles", w, h, body, defs)


banner(); divider(); about(); principles()
for s, l, c in [("about", "About", LAV), ("focus", "Current focus", SAGE), ("projects", "Open-source projects", PEACH),
                ("activity", "Activity", PEACH), ("stack", "Toolbox", ROSE), ("certs", "Certifications", LAV), ("connect", "Connect", SAGE)]:
    heading(s, l, c)
button("github", "GitHub", "@CodeByPinar", "github", LAV)
button("linkedin", "LinkedIn", "in/pinardev", "linkedin", SAGE)
button("mail", "E-mail", "piinartp@gmail.com", "mail", ROSE)
button("x", "X", "@pinariisko", "x", LAV)
button("instagram", "Instagram", "@pinariisko", "insta", PEACH)
card("surge", "Surge", "GLPI PLUGIN",
     ["Detects bursts of similar tickets and", "groups them into one major incident.", "GLPI 11 + 12, six UI languages."],
     ["PHP", "TF-IDF", "GPLv3"], LAV)
card("guard", "glpi-guard", "SECURITY AUDITOR",
     ["Read-only GLPI auditor: 25 checks, score", "and remediation steps. CLI + plugin,", "offline advisory database."],
     ["PHP", "CLI", "CI-ready"], SAGE)
card("scaffold", "create-glpi-plugin", "DEV TOOL",
     ["One npx command scaffolds a GLPI 11/12", "plugin: hooks, CSRF-safe forms, i18n", "and AI coding rules included."],
     ["Node", "npm", "Templates"], PEACH)
stack(); certs(); focus(); footer()
print("assets ->", os.path.abspath(OUT))
