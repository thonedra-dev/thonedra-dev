"""Build the current profile artwork without regenerating the supplied portrait.

Python creates native SVG compositions. Node/resvg rasterizes only the two hero
compositions to standalone PNGs for dependable Markdown image rendering.
Run: python tools/build_assets.py [--render-tools PATH_TO_NPM_PREFIX]
"""

import argparse
import base64
from html import escape
import math
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PREVIEW = ROOT / ".preview"
BG, SURFACE = "#080B10", "#111722"
WHITE, SILVER = "#F2F5FA", "#A7B2C2"
BLUE, ICE, STEEL = "#4DA3FF", "#8EDBFF", "#253244"


def text(x, y, value, size=16, fill=SILVER, weight=400, tracking=0):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" letter-spacing="{tracking}">{escape(value)}</text>')


def path(d, stroke=STEEL, width=1, fill="none", extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def rect(x, y, w, h, fill=SURFACE, stroke=STEEL, radius=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def dot(x, y, r=3, fill=ICE):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


def label(x, y, value, size=14):
    return text(x, y, value, size, ICE, 400, 2)


def monogram(x, y, scale=1):
    return (f'<g transform="translate({x} {y}) scale({scale})" fill="none" '
            f'stroke="{ICE}" stroke-width="1.5">'
            '<path d="M0 10 17 0 34 10 17 20Z M8 15V29L17 34V20 M26 15V29L17 34"/></g>')


def document(name, width, height, title, desc, content, working=False):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs>
  <linearGradient id="surface" x2="1" y2="1"><stop stop-color="{BG}"/><stop offset="1" stop-color="{SURFACE}"/></linearGradient>
  <radialGradient id="light" cx="82%" cy="32%" r="62%"><stop stop-color="{BLUE}" stop-opacity=".14"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
  <radialGradient id="warm" cx="78%" cy="26%" r="35%"><stop stop-color="#FFB976" stop-opacity=".07"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
  <linearGradient id="edge"><stop stop-color="{BLUE}" stop-opacity="0"/><stop offset=".55" stop-color="{ICE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
</defs>
<g font-family="Arial, Helvetica, sans-serif">
  <rect width="{width}" height="{height}" rx="4" fill="url(#surface)"/>
  <rect width="{width}" height="{height}" rx="4" fill="url(#light)"/>
  <rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="4" fill="none" stroke="{STEEL}"/>
  {content}
</g></svg>
'''
    folder = PREVIEW if working else ASSETS
    folder.mkdir(exist_ok=True)
    target = folder / name
    target.write_text(svg, encoding="utf-8", newline="\n")
    return target


def portrait(x, y, width):
    # The original PNG is embedded byte-for-byte. Only uniform scale/translation
    # are applied; there is no crop, retouching, recoloring, or generative edit.
    data = base64.b64encode((ASSETS / "thone-dra-portrait.png").read_bytes()).decode("ascii")
    height = width * 1175 / 1339
    return (f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{data}"/>')


def tool_group(category, tools, x, title_y, width, cols, mobile=False):
    s = text(x, title_y, category, 24, WHITE)
    step = width / cols
    for i, (name, slug) in enumerate(tools):
        tx, ty = x+(i % cols)*step, title_y+25+(i//cols)*51
        s += tech_icon(name, slug, tx, ty, 32)
        s += text(tx+44, ty+26, name, 22 if mobile else 23)
    return s


def heroes():
    # A single background, border, lighting field, and alignment grid span the
    # portrait, introduction, focus, and toolkit. There is no second banner.
    s = '<rect width="1000" height="1272" fill="url(#warm)"/>'
    s += monogram(46, 34, .65) + label(82, 51, "THE ARCHITECT")
    s += path("M506 84V425 M530 84h18 M530 425h18", STEEL)
    s += path("M550 112H954 M550 425H954", STEEL, .7)
    s += portrait(480, 80, 500)
    s += text(40, 207, "THONE", 120, WHITE, 600, -6)
    s += text(40, 320, "DRA", 120, WHITE, 600, -6)
    s += text(48, 370, "Software engineering", 24)
    s += text(48, 402, "Full-stack development", 24)
    s += text(48, 452, "Final-year Computer Science undergraduate", 20)
    s += text(48, 481, "Albukhary International University", 20)
    s += text(48, 510, "Malaysia", 20)
    s += text(48, 555, "Seeking Software Engineering internships.", 21, ICE)
    s += path("M48 586H952", "url(#edge)")
    s += text(48, 624, "BACKEND ARCHITECTURE / DATABASES / AUTHENTICATION / USER EXPERIENCES", 17, SILVER, 400, .7)
    s += label(48, 674, "THE ENGINEERING TOOLKIT", 16)
    s += tool_group(*TOOLKIT[0], 48, 720, 904, 4)
    s += path("M48 800H952", STEEL)
    s += tool_group(*TOOLKIT[1], 48, 845, 904, 3)
    s += path("M48 975H952", STEEL)
    s += tool_group(*TOOLKIT[2], 48, 1020, 452, 2)
    s += tool_group(*TOOLKIT[3], 528, 1020, 424, 2)
    s += path("M48 1100H952 M500 1000V1080", STEEL)
    s += tool_group(*TOOLKIT[4], 48, 1146, 904, 4)
    s += text(48, 1240, "Engineering with intent. Experience varies by technology.", 17)
    document("hero-layout.svg", 1000, 1272, "Thone Dra - identity and engineering capabilities",
             "One seamless personal composition: portrait, professional identity, education, internship goal, engineering interests, and all 18 technologies.", s, True)

    s = '<rect width="480" height="1728" fill="url(#warm)"/>'
    s += monogram(28, 25, .6) + label(61, 42, "THE ARCHITECT", 13)
    s += text(24, 119, "THONE DRA", 63, WHITE, 600, -3)
    s += text(30, 156, "Software engineering", 23)
    s += text(30, 187, "Full-stack development", 23)
    s += path("M30 249V559 M450 249V559", STEEL, .7)
    s += portrait(28, 227, 424)
    s += text(28, 640, "Final-year Computer Science undergraduate", 20)
    s += text(28, 675, "Albukhary International University", 21)
    s += text(28, 705, "Malaysia", 21)
    s += text(28, 747, "Seeking Software Engineering internships.", 21, ICE)
    s += path("M28 772H452", "url(#edge)")
    s += text(28, 808, "Backend architecture / Databases", 20)
    s += text(28, 838, "Authentication / User experiences", 20)
    s += label(28, 887, "THE ENGINEERING TOOLKIT", 15)
    for i, (category, tools) in enumerate(TOOLKIT):
        y = (931, 1098, 1316, 1432, 1548)[i]
        s += tool_group(category, tools, 28, y, 424, 2, True)
        if i < 4:
            bottom = y+25+math.ceil(len(tools)/2)*51+11
            s += path(f"M28 {bottom}H452", STEEL)
    s += text(28, 1696, "Experience varies by technology.", 19)
    document("hero-mobile-layout.svg", 480, 1728, "Thone Dra - identity and engineering capabilities",
             "A portrait arrangement of the same complete personal presentation. The original face and waving hand remain fully visible.", s, True)


TOOLKIT = (
    ("Programming languages", (("Python", "python"), ("JavaScript", "javascript"), ("PHP", "php"), ("SQL", None))),
    ("Frontend engineering", (("React", "react"), ("Next.js", "nextdotjs"), ("Inertia.js", "inertia"), ("Tailwind CSS", "tailwindcss"), ("HTML", "html5"), ("CSS", "css"))),
    ("Backend engineering", (("Laravel", "laravel"), ("Flask", "flask"))),
    ("Database systems", (("PostgreSQL", "postgresql"), ("MySQL", "mysql"))),
    ("Development tools", (("Git", "git"), ("GitHub", "github"), ("VS Code", None), ("Vite", "vite"))),
)


def tech_icon(name, slug, x, y, size=27):
    if slug:
        source = ET.parse(ASSETS / "icons" / f"{slug}.svg").getroot()
        shapes = ''.join(f'<path d="{escape(el.get("d"), quote=True)}"/>' for el in source.iter() if el.tag.endswith('path'))
        return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{ICE}">{shapes}</svg>'
    return rect(x, y, size, size, "none", BLUE, 4) + text(x+3, y+size*.67, "DB" if name=="SQL" else "VS", size*.43, ICE, 600)


def work_icon(kind, cx, cy):
    if kind == "institution":
        s = path(f"M{cx-50} {cy-18}H{cx+50} M{cx} {cy-18}V{cy+32} M{cx-50} {cy-18}V{cy+25} M{cx+50} {cy-18}V{cy+25}", BLUE, 1.5)
        for dx, dy in ((0,-18),(-50,30),(0,30),(50,30)):
            s += rect(cx+dx-13, cy+dy-11, 26, 22, "#192D43", BLUE, 3)
        return s
    if kind == "cinema":
        s = path(f"M{cx-55} {cy-29}Q{cx} {cy-43} {cx+55} {cy-29}", ICE, 2)
        for row in range(3):
            for col in range(6):
                s += rect(cx-53+col*19, cy-7+row*18, 12, 10, ICE if row==1 and col==3 else "#29445F", "none", 2)
        return s
    if kind == "tasks":
        s = ""
        for col in range(3):
            xx = cx-60+col*43
            s += rect(xx, cy-32, 35, 72, "#122032", STEEL, 3)
            s += path(f"M{xx+6} {cy-21}h23", BLUE, 2)
            for row in range(2 if col<2 else 1):
                s += rect(xx+6, cy-9+row*20, 23, 13, "#29445F", "none", 2)
        return s
    return (path(f"M{cx-43} {cy-9}h86l-8 51h-70Z", BLUE, 1.5, "#192D43")
            + path(f"M{cx-22} {cy-2}v-23q22-27 44 0v23", ICE, 1.5))


def selected_work():
    items = (
        ("01", "Vantage", "institution",
         ("Self-hosted institutional intranet.", "Role-based access. Data sovereignty."),
         ("Laravel / PostgreSQL", "Inertia.js / React"), "Under development / FYP"),
        ("02", "Cinema X", "cinema",
         ("Cinema management & reservations.", "Dynamic pricing and payments."),
         ("Laravel / PostgreSQL / JavaScript",), ""),
        ("03", "TaskFlow", "tasks",
         ("Full-stack productivity.", "Tasks, meetings & collaboration."),
         ("React / Flask / MySQL",), ""),
        ("04", "Aureli", "commerce",
         ("Full-stack e-commerce.", "Products, carts & customer journeys."),
         ("React / Flask / MySQL",), ""),
    )
    for mobile in (False, True):
        width, height = (480, 1216) if mobile else (1000, 744)
        x0 = 28 if mobile else 48
        s = label(x0, 42, "SELECTED WORK", 14)
        s += text(x0, 84, "Four systems. One engineering mind.", 23 if mobile else 34, WHITE, 400, -.5)
        for i, (number, name, kind, lines, tech, status) in enumerate(items):
            xx = 28 if mobile else 48+(i%2)*480
            yy = (114, 408, 672, 936)[i] if mobile else 120+(i//2)*302
            card_height = 278 if not mobile or i == 0 else 248
            s += rect(xx, yy, 424, card_height, "#0C131E", STEEL, 4)
            s += label(xx+20, yy+30, number, 14)
            s += text(xx+20, yy+80, name, 38, WHITE, 500, -1)
            s += f'<g transform="translate({xx+365} {yy+59}) scale(.55)">{work_icon(kind, 0, 0)}</g>'
            for j, line in enumerate(lines):
                s += text(xx+20, yy+121+j*31, line, 21, SILVER)
            for j, line in enumerate(tech):
                s += text(xx+20, yy+196+j*29, line, 21, ICE)
            if status:
                s += text(xx+20, yy+258, status, 20, SILVER)
        document("selected-work-mobile.svg" if mobile else "selected-work.svg", width, height,
                 "Selected work - Vantage, Cinema X, TaskFlow, and Aureli",
                 "Four project names, domain illustrations, complete short descriptions, primary technologies, and Vantage development status in one composition.", s)


def footer():
    s = path("M44 29H956", "url(#edge)")
    s += text(42, 88, "Built with intent.", 43, WHITE, 400, -1)
    s += label(44, 121, "THONE DRA / THE ARCHITECT", 12)
    s += monogram(866, 56, 1.25)
    document("footer.svg", 1000, 150, "Built with intent", "Thone Dra - The Architect.", s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-tools", type=Path, default=Path(tempfile.gettempdir()) / "architect-profile-render",
                        help="npm prefix containing @resvg/resvg-js; see docs/PROFILE_REVIEW.md")
    args = parser.parse_args()
    heroes()
    selected_work()
    footer()
    subprocess.run(["node", str(ROOT / "tools" / "render_heroes.mjs"), str(args.render_tools)], cwd=ROOT, check=True)
    for asset in sorted(ASSETS.iterdir()):
        if asset.is_file():
            print(f"{asset.relative_to(ROOT)}: {asset.stat().st_size:,} bytes")
