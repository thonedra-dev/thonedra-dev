"""Check local profile references, SVG safety, and preserved metrics files.

Run: python tools/validate_profile.py
This does not simulate GitHub's sanitizer or execute a GitHub Actions job.
"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import ast
import hashlib
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
SVG = "{http://www.w3.org/2000/svg}"
errors = []
references = []
markdown = (ROOT / "README.md").read_text(encoding="utf-8")


def check(condition, message):
    if not condition:
        errors.append(message)


class ProfileHTML(HTMLParser):
    allowed = {"picture", "source", "img", "p", "details", "summary", "br"}

    def handle_starttag(self, tag, attrs):
        check(tag in self.allowed, f"Unsupported profile HTML: {tag}")
        attrs = dict(attrs)
        check(not any(k in {"style", "class", "id"} or k.startswith("on") for k in attrs), f"Sanitizer-sensitive HTML attributes: {tag}")
        if tag == "img":
            check(bool(attrs.get("alt", "").strip()), "HTML image needs meaningful alt text")
            references.append(attrs.get("src", ""))
        elif tag == "source":
            references.extend(part.strip().split()[0] for part in attrs.get("srcset", "").split(",") if part.strip())


ProfileHTML().feed(markdown)
for alt, source in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", markdown):
    check(bool(alt.strip()), f"Markdown image needs meaningful alt text: {source}")
    references.append(source)

headings = [name.strip() for name in re.findall(r"^#{1,6}\s+(.+)$", markdown, re.M)]
slugs = {re.sub(r"[^\w\- ]", "", name.lower()).replace(" ", "-") for name in headings}
links = re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", markdown)
for target in links:
    if target.startswith("#"):
        check(target[1:] in slugs, f"Unknown section anchor: {target}")
    elif urlparse(target).scheme:
        check(target.startswith("https://"), f"Non-HTTPS outbound link: {target}")
    else:
        references.append(target)

for reference in sorted(set(references)):
    check(not urlparse(reference).scheme, f"Remote image dependency: {reference}")
    candidate = ROOT / unquote(reference)
    check(candidate.resolve().is_relative_to(ROOT), f"Reference leaves repository: {reference}")
    check(candidate.is_file(), f"Missing local asset: {reference}")
    current = ROOT
    for part in Path(reference).parts:
        if current.is_dir():
            check(part in {p.name for p in current.iterdir()}, f"Case mismatch in local reference: {reference}")
        current /= part

assets = sorted((ROOT / "assets").glob("*.svg"))
for asset in assets:
    check(f"assets/{asset.name}" in markdown, f"Unused generated asset: {asset.name}")
    tree = ET.parse(asset).getroot()
    check(tree.tag == SVG + "svg", f"Wrong SVG root: {asset.name}")
    check(tree.get("viewBox") is not None, f"Missing responsive viewBox: {asset.name}")
    check(tree.findtext(SVG + "title"), f"Missing SVG title: {asset.name}")
    check(tree.findtext(SVG + "desc"), f"Missing SVG description: {asset.name}")
    ids = [el.get("id") for el in tree.iter() if el.get("id")]
    check(len(ids) == len(set(ids)), f"Duplicate SVG IDs: {asset.name}")
    for element in tree.iter():
        kind = element.tag.rsplit("}", 1)[-1]
        check(kind not in {"script", "foreignObject", "image", "animate", "animateTransform", "set", "style"}, f"Non-static or embedded content: {asset.name}: {kind}")
        for key, value in element.attrib.items():
            check(not key.startswith("on"), f"SVG event handler: {asset.name}")
            check("href" not in key or value.startswith("#"), f"External SVG reference: {asset.name}")
            for fragment in re.findall(r"url\(#([^)]+)\)", value):
                check(fragment in ids, f"Unresolved SVG reference #{fragment}: {asset.name}")


def validate_png(asset, expected_size):
    data = asset.read_bytes()
    check(data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature: {asset.name}")
    check(struct.unpack(">II", data[16:24]) == expected_size, f"Unexpected PNG dimensions: {asset.name}")
    position = 8
    chunk_kinds = []
    while position < len(data):
        size = struct.unpack(">I", data[position:position+4])[0]
        kind = data[position+4:position+8]
        chunk = data[position+4:position+8+size]
        crc = struct.unpack(">I", data[position+8+size:position+12+size])[0]
        check(zlib.crc32(chunk) & 0xffffffff == crc, f"PNG chunk checksum failed: {asset.name}")
        chunk_kinds.append(kind)
        position += size+12
    check(b"IDAT" in chunk_kinds and chunk_kinds[-1] == b"IEND", f"Incomplete PNG: {asset.name}")


validate_png(ROOT / "assets/hero.png", (2000, 2544))
validate_png(ROOT / "assets/hero-mobile.png", (960, 3456))
portrait = ROOT / "assets/thone-dra-portrait.png"
validate_png(portrait, (1339, 1175))
check(portrait.read_bytes()[25] == 6, "Portrait must retain its original RGBA color type")
check(hashlib.sha256(portrait.read_bytes()).hexdigest().upper() ==
      "BBE6D7E7BAD7A08ECCB5B1ACB8A46CE14FE41E34056A7CCBDE5F74422529D799",
      "Supplied portrait bytes have changed")
build_source = (ROOT / "tools/build_assets.py").read_text(encoding="utf-8")
for asset in (ROOT / "assets").glob("*.png"):
    check(f"assets/{asset.name}" in markdown or asset.name in build_source,
          f"Unused PNG asset: {asset.name}")

# Source icons are build inputs, not network dependencies at display time.
for icon in (ROOT / "assets" / "icons").glob("*.svg"):
    ET.parse(icon)
    check(f'"{icon.stem}"' in (ROOT / "tools" / "build_assets.py").read_text(encoding="utf-8"), f"Unused source icon: {icon.name}")
check("<details>" not in markdown[markdown.index("## GitHub activity"):], "Metrics must remain visible by default")
check("?" not in markdown, "Unexpected question mark: check text encoding")
check("AIU Vantage" not in markdown, "Use the final project name Vantage")
check("**+60 11 2892 2047**" in markdown and "https://wa.me/601128922047" in markdown,
      "Phone and WhatsApp contact must match the supplied number")
check("github.com/thonedra-dev/" not in markdown, "Project repository links are not part of the final visual showcase")
ET.parse(ROOT / "github-metrics.svg")
for source in (ROOT / "tools").glob("*.py"):
    ast.parse(source.read_text(encoding="utf-8"), filename=str(source))

preserved = subprocess.run(
    ["git", "diff", "--exit-code", "HEAD", "--", ".github/workflows/metrics.yml", "github-metrics.svg"],
    cwd=ROOT, capture_output=True, text=True,
)
check(preserved.returncode == 0, "Existing metrics workflow or generated SVG differs from HEAD")

if errors:
    raise SystemExit("Validation failed:\n- " + "\n- ".join(errors))
print(f"PASS: {len(assets)} SVGs parsed; titles, descriptions, IDs, and static content checked.")
print("PASS: PNG dimensions and chunk checksums; supplied RGBA portrait is byte-for-byte unchanged.")
print(f"PASS: {len(set(references))} local references exist with exact filename casing; image alt text and section anchors checked.")
print("PASS: Python sources parse; metrics SVG parses; existing metrics files match HEAD.")
print("GitHub production rendering, external link availability, and Actions execution require separate review.")
