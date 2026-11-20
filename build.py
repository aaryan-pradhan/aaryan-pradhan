#!/usr/bin/env python3
"""Draw profile.svg: a pixel-art, line-numbered page in the style of
pokerbot.sequoiacap.com. Light and dark themes live in the one file.

    python3 build.py        # needs GITHUB_TOKEN or a logged-in `gh`
"""
import datetime, json, os, subprocess, urllib.request

USER = "aaryan-pradhan"
W, X, CW = 880, 60, 800      # canvas width, text column x, text column width
ROW = 24                      # height of one numbered line

LETTERHEAD = ["AARYAN PRADHAN", "IIT KHARAGPUR, CLASS OF 2027", "BOMBAY 400076"]
HELLO = "HI, I TINKER WITH OPEN-SOURCE SOFTWARE."
ABOUT = [
    "> ON LINUX SINCE 5TH GRADE (MINT XFCE, ARCH).",
    "> I BUILD WEB APPS, ML MODELS AND SMALL TOOLS.",
    "> I WRITE MATH NOTES LIKE EUCLID: AXIOMS, THEN PROOFS.",
]
STACK = [
    ("LANGUAGES", ["PYTHON", "C++", "C", "C#", "RUST", "JAVA", "TYPESCRIPT", "JAVASCRIPT", "R", "BASH"]),
    ("WEB", ["REACT", "NODE", "EXPRESS", "DJANGO", "TAILWIND", "VITE", "FIREBASE"]),
    ("DATA", ["POSTGRES", "MONGODB", "REDIS", "CELERY", "BULLMQ"]),
    ("ML", ["PYTORCH", "SCIKIT-LEARN", "NUMPY", "SCIPY", "LIGHTGBM", "JUPYTER"]),
    ("TOOLS", ["DOCKER", "GIT", "LINUX MINT", "ARCH", "LATEX", "VITEST"]),
]

# 5x7 pixel font, rows top to bottom.
FONT = {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .####",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# #...# ##..# #.#.# #..## #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "####. ....# ....# .###. ....# ....# ####.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": "..##. .#... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. .#... .#... .#...",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ...#. .##..",
    ".": "..... ..... ..... ..... ..... .##.. .##..",
    ",": "..... ..... ..... ..... .##.. ..#.. .#...",
    ":": "..... .##.. .##.. ..... .##.. .##.. .....",
    "'": "..#.. ..#.. .#... ..... ..... ..... .....",
    "-": "..... ..... ..... .###. ..... ..... .....",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    ">": ".#... ..#.. ...#. ....# ...#. ..#.. .#...",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "#": ".#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.",
    "(": "...#. ..#.. .#... .#... .#... ..#.. ...#.",
    ")": ".#... ..#.. ...#. ...#. ...#. ..#.. .#...",
    "=": "..... ..... ##### ..... ##### ..... .....",
}

# 12x13 penguin. o outline, k back, w belly, e pupil, y beak and feet.
PENGUIN = [
    "....oooo....",
    "...okkkko...",
    "..okkkkkko..",
    "..owekweko..",
    "..okyyyyko..",
    ".okwwyywwko.",
    ".okwwwwwwko.",
    "okkwwwwwwkko",
    "okkwwwwwwkko",
    ".okwwwwwwko.",
    "..okwwwwko..",
    "...oooooo...",
]
FEET = ["..yyy..yyy..", "...yy..yy..."]
SPRITE_FILL = {"k": "#1b1b1b", "w": "#ffffff", "e": "#000000", "y": "#ffc400"}

CSS = """
svg{--paper:#ffffff;--ink:#111111;--grey:#8a8a8a}
@media (prefers-color-scheme:dark){svg{--paper:#0d1117;--ink:#e6edf3;--grey:#6e7681}}
.p{fill:var(--paper)}.i{fill:var(--ink)}.g{fill:var(--grey)}
.blink{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
"""


def runs(rows, on):
    """Path of horizontal pixel runs where rows[r][c] is in `on`."""
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] in on:
                n = 1
                while c + n < len(row) and row[c + n] in on:
                    n += 1
                d.append(f"M{c} {r}h{n}v1h-{n}z")
                c += n
            else:
                c += 1
    return "".join(d)


def width(s, scale=2):
    return len(s) * 6 * scale - scale


def text(s, x, y, cls, scale=2):
    missing = set(s) - set(FONT) - {" "}
    assert not missing, f"no glyph for {missing}"
    uses = "".join(f'<use href="#g{ord(ch)}" x="{i * 6}"/>' for i, ch in enumerate(s) if ch != " ")
    return f'<g class="{cls}" transform="translate({x} {y}) scale({scale})">{uses}</g>'


def sprite(feet, outline, dy=0):
    rows = PENGUIN + [feet]
    paths = [f'<path class="{outline}" d="{runs(rows, "o")}"/>']
    paths += [f'<path fill="{f}" d="{runs(rows, c)}"/>' for c, f in SPRITE_FILL.items()]
    return f'<g transform="translate(0 {dy})">{"".join(paths)}</g>'


def discrete(attr, values, times, repeat=True):
    end = 'repeatCount="indefinite"' if repeat else 'fill="freeze"'
    kt = ";".join(f"{t:.4f}" for t in times)
    return f'<animate attributeName="{attr}" calcMode="discrete" values="{";".join(map(str, values))}" keyTimes="{kt}" dur="{{dur}}s" {end}/>'


def longest_streak(days):
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] else 0
        best = max(best, cur)
    return best


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    query = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
             'weeks{contributionDays{contributionCount contributionLevel weekday}}}}}}' % USER)
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": query}).encode(),
                                 {"Authorization": f"bearer {token}"})
    data = json.load(urllib.request.urlopen(req))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
SHADE = [0.14, 0.4, 0.6, 0.8, 1]


def render(cal, today):
    out, defs = [], []
    ids = iter(range(10**6))
    y, n = 20, 0

    def line(cls="i", left="", right="", center="", h=ROW, number=True):
        nonlocal y, n
        if number:
            n += 1
            out.append(text(str(n), 40 - width(str(n), 1), y + 9, "g", 1))
        ty = y + (ROW - 14) // 2
        if left:
            out.append(text(left, X, ty, cls))
        if right:
            out.append(text(right, X + CW - width(right), ty, cls))
        if center:
            out.append(text(center, X + (CW - width(center)) // 2, ty, cls))
        y += h

    def typed(s, x, ty, cls, t0, step, dur, repeat):
        cid = f"c{next(ids)}"
        times = [0] + [(t0 + j * step) / dur for j in range(len(s) + 1)]
        anim = discrete("width", [0] + [j * 12 for j in range(len(s) + 1)], times, repeat).format(dur=dur)
        defs.append(f'<clipPath id="{cid}"><rect x="{x - 1}" y="{ty - 2}" height="18" width="0">{anim}</rect></clipPath>')
        return f'<g clip-path="url(#{cid})">{text(s, x, ty, cls)}</g>'

    rule = "=" * (CW // 12)

    # Letterhead, on paper.
    for s in LETTERHEAD:
        line(left=s)
    head_y = y - 3 * ROW
    blink = discrete("opacity", [0, 1, 0], [0, 0.96, 0.99]).format(dur=5)
    out.append(f'<g transform="translate({X + CW - 48} {head_y}) scale(4)">{sprite(FEET[0], "i")}'
               f'<path fill="#1b1b1b" opacity="0" d="M3 3h2v1h-2zM6 3h2v1h-2z">{blink}</path></g>')
    line(number=True)
    ty = y + 5
    step, t0 = 0.05, 0.4
    dur = t0 + len(HELLO) * step
    out.append(f'<rect class="i" x="{X - 8}" y="{y}" width="{width(HELLO) + 30}" height="{ROW}"/>')
    out.append(typed(HELLO, X, ty, "p", t0, step, dur, repeat=False))
    xs = [X] + [X + j * 12 for j in range(len(HELLO) + 1)]
    times = [0] + [(t0 + j * step) / dur for j in range(len(HELLO) + 1)]
    out.append(f'<rect class="p blink" y="{ty}" width="10" height="14" x="{X}">'
               f'{discrete("x", xs, times, repeat=False).format(dur=dur)}</rect>')
    line()
    line()
    line(left=rule, cls="g")
    line()

    line()
    line(center="EXHIBIT A: A YEAR OF CODE", cls="i")
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    line(left="365 DAYS, ONE PENGUIN", right="UPDATED DAILY", cls="i")
    line(left=f"CONTRIBUTIONS: {cal['totalContributions']:,}",
         right=f"LONGEST STREAK: {longest_streak(days)} DAYS", cls="i")

    # Contribution grid. A penguin walks it week by week, lighting each column.
    weeks = cal["weeks"]
    gx = X + (CW - (len(weeks) * 13 - 3)) // 2
    gy = y + 34
    ghost, lit = [], []
    for c, w in enumerate(weeks):
        for d in w["contributionDays"]:
            cell = f'x="{gx + c * 13}" y="{gy + d["weekday"] * 13}" width="10" height="10"'
            ghost.append(f'<rect {cell} opacity="{SHADE[0]}"/>')
            lit.append(f'<rect {cell} opacity="{SHADE[LEVEL[d["contributionLevel"]]]}"/>')
    T, walk = 16, 0.6
    times = [walk * k / len(weeks) for k in range(len(weeks) + 1)]
    reveal = discrete("width", [k * 13 for k in range(len(weeks) + 1)], times).format(dur=T)
    defs.append(f'<clipPath id="walk"><rect x="{gx}" y="{gy}" height="91" width="0">{reveal}</rect></clipPath>')
    out.append(f'<g class="i">{"".join(ghost)}</g><g class="i" clip-path="url(#walk)">{"".join(lit)}</g>')
    py = gy - 30
    pos = [f"{gx - 34},{py}"] + [f"{gx + (k - 1) * 13 - 7},{py}" for k in range(1, len(weeks) + 1)]
    frame_a = ["visible" if k % 2 == 0 or k == len(weeks) else "hidden" for k in range(len(weeks) + 1)]
    frame_b = ["hidden" if v == "visible" else "visible" for v in frame_a]
    out.append(
        f'<g><animateTransform attributeName="transform" type="translate" calcMode="discrete" '
        f'values="{";".join(pos)}" keyTimes="{";".join(f"{t:.4f}" for t in times)}" dur="{T}s" repeatCount="indefinite"/>'
        f'<g transform="scale(2)">'
        f'<g>{sprite(FEET[0], "i")}{discrete("visibility", frame_a, times).format(dur=T)}</g>'
        f'<g visibility="hidden">{sprite(FEET[1], "i", -1)}{discrete("visibility", frame_b, times).format(dur=T)}</g>'
        f'</g></g>')
    y = gy + 91 + 12
    legend_y = y + 5
    out.append(text("LESS", X, legend_y, "i"))
    for i, s in enumerate(SHADE):
        out.append(f'<rect class="i" x="{X + 60 + i * 16}" y="{legend_y + 2}" width="10" height="10" opacity="{s}"/>')
    out.append(text("MORE", X + 60 + 5 * 16 + 6, legend_y, "i"))
    line()
    line()
    line(left=rule, cls="g")
    line()

    # About me: typed line by line, held, then typed again.
    line(center="EXHIBIT B: ABOUT ME", cls="i")
    line()
    T2, step = 15, 0.045
    t, events = 0.6, [(0, X, y + 5)]
    for i, s in enumerate(ABOUT):
        ty = y + 5
        out.append(typed(s, X, ty, "i", t, step, T2, repeat=True))
        events += [(t + j * step, X + j * 12, ty) for j in range(len(s) + 1)]
        t += len(s) * step + 0.5
        line()
    ts = [e[0] / T2 for e in events]
    out.append(f'<rect class="i blink" width="10" height="14" x="{X}" y="{events[0][2]}">'
               f'{discrete("x", [e[1] for e in events], ts).format(dur=T2)}'
               f'{discrete("y", [e[2] for e in events], ts).format(dur=T2)}</rect>')
    line()
    line(left=rule, cls="g")
    line()

    # Stack: a selection box sweeps across the tiles, like pokerbot's speed toggle.
    line(center="EXHIBIT C: STACK", cls="i")
    line()
    tiles = []
    for label, items in STACK:
        tx = X + 132
        out.append(text(label, X, y + 5, "g"))
        for item in items:
            w = width(item) + 16
            if tx + w > X + CW:
                line(h=ROW + 8)
                tx = X + 132
            tiles.append((tx, y, item, w))
            tx += w + 8
        line(h=ROW + 8)
    slot, hold = 0.22, 6
    D = len(tiles) * slot + hold
    at = 100 * slot / D
    css = [f"@keyframes hb{{0%{{fill:var(--ink)}}{at:.2f}%{{fill:var(--paper)}}}}",
           f"@keyframes hf{{0%{{fill:var(--paper)}}{at:.2f}%{{fill:var(--ink)}}}}",
           f".tb{{fill:var(--paper);stroke:var(--ink);stroke-width:2;animation:hb {D:.2f}s steps(1) infinite}}",
           f".tf{{fill:var(--ink);animation:hf {D:.2f}s steps(1) infinite}}"]
    for k, (tx, ty, item, w) in enumerate(tiles):
        delay = f"animation-delay:{k * slot:.2f}s"
        out.append(f'<rect class="tb" style="{delay}" x="{tx}" y="{ty + 1}" width="{w}" height="22"/>')
        out.append(text(item, tx + 8, ty + 5, "tf").replace('class="tf"', f'class="tf" style="{delay}"'))
    line(left=rule, cls="g")
    line(left=f"LAST UPDATED {today.isoformat()}", right="END OF FILE", cls="g")
    y += 12

    glyphs = "".join(f'<path id="g{ord(c)}" d="{runs(rows.split(), "#")}"/>' for c, rows in FONT.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {y}" width="{W}" height="{y}" '
            f'shape-rendering="crispEdges" role="img" aria-label="Aaryan Pradhan, IIT Kharagpur, class of 2027">'
            f'<title>Aaryan Pradhan</title><style>{CSS}{"".join(css)}</style>'
            f'<defs>{glyphs}{"".join(defs)}</defs><rect class="p" width="{W}" height="{y}"/>{"".join(out)}</svg>')


if __name__ == "__main__":
    with open("profile.svg", "w") as f:
        f.write(render(fetch(), datetime.date.today()))
