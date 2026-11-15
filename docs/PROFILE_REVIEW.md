# THE ARCHITECT - unified visual portfolio

Updated 15 November 2026. One README on `cinematic-profile-redesign`.
The local review was completed before staging or publishing. On 16 November 2026,
the user authorized committing and pushing the completed branch for their own PR.

## Final composition

The opening is one continuous personal-brand image: portrait, name, professional
identity, education, internship goal, engineering interests, and all 18 tools.
A single background, lighting field, border, and alignment grid span the whole
composition. There is no separate About banner or intervening Markdown copy.

The second composition contains the complete four-project showcase. Each project
has an original domain icon, name, description, and primary technologies. The
desktop grid uses two columns; the mobile composition uses one column with
larger type. Vantage is marked under development. Repository links and repeated
visible project paragraphs have been removed as requested.

An optional collapsed **Accessible text version** provides the same identity,
toolkit, and project information as native text. It is the sole text equivalent;
it does not repeat the image contents in the default visual layout. The only
standalone visible text sections are GitHub Activity and Connect.

Connect preserves LinkedIn and GitHub and adds **+60 11 2892 2047**, linked to
WhatsApp through the supplied `https://wa.me/601128922047` URL. No message has
been sent. The portrait, palette, type families, and original icon sources remain.

## Current files

| File | Purpose |
| :--- | :--- |
| README.md | Two major visuals, accessible text equivalent, activity, and contacts |
| assets/hero.png | Complete desktop identity/introduction/toolkit composition |
| assets/hero-mobile.png | Responsive portrait arrangement of that composition |
| assets/selected-work.svg | Four-project showcase with descriptions and stacks |
| assets/selected-work-mobile.svg | Single-column arrangement with readable content |
| assets/footer.svg | Existing compact brand signature |
| assets/thone-dra-portrait.png | Unmodified portrait source with transparency |
| assets/icons/*.svg | Sixteen reused, local technology icon sources |
| assets/icons/LICENSE.md | Retained upstream CC0 license |
| assets/icons/README.md | Icon provenance and update instructions |
| tools/build_assets.py | Current compositions and complete artwork build |
| tools/render_heroes.mjs | resvg rasterization and lossless PNG recompression |
| tools/validate_profile.py | SVG, PNG, identity, contact, and preservation checks |
| .gitignore | Excludes local review artifacts |
| docs/PROFILE_REVIEW.md | Current design and verification notes |

The separate About SVGs and unused preview images are removed after checking
replacement references. No competing README or old production layout is kept.
Responsive images represent the same final design.

## Portrait and rendering

The portrait source retains its original 1339 x 1175 RGBA pixels and SHA-256:

```text
BBE6D7E7BAD7A08ECCB5B1ACB8A46CE14FE41E34056A7CCBDE5F74422529D799
```

It is uniformly scaled and placed, with the entire face and waving hand visible.
There is no generative image step, recoloring, retouching, or stretching. Source
alpha remains intact; the completed compositions have opaque obsidian backgrounds.

Identity PNGs render at 2000 x 2544 and 960 x 3456, then are losslessly recompressed.
These self-contained PNGs avoid raster-image nesting inside SVGs. The project
showcase remains vector artwork. Both compositions switch to portrait layouts
at viewport widths of 760px or less. A 2x-density PNG source preserves sharpness
while keeping both portrait compositions at their intended maximum display
width of 480px, avoiding oversized tablet scaling. Core mobile project text is 21px in the
480px-wide artwork; mobile technology labels are 22px. Layouts prioritize
legibility over a crowded mobile grid.

## Automation and accuracy

`.github/workflows/metrics.yml` and `github-metrics.svg` remain byte-for-byte
unchanged. Schedule, manual dispatch, token reference, main-branch output,
timezone, and plugins remain intact. YAML is parsed locally; a live Actions job
has not been run.

```text
metrics.yml: DE47F1DA1D153E279CFA703DDE8A4BBE67CB4DB8473408BBA158B8BE5BF11F72
github-metrics.svg: 7E46A36C9FAF60AEF934CFCE4FD2DAA90FD3E9A60025A6B3634168C0D460A8BB
```

Metrics stay visible by default. The isometric contributions calendar differs
from GitHub's traditional heatmap. Existing palette, data, and the empty language
section remain unchanged. A full-size link supports narrow-screen viewing.

The institutional project is named **Vantage** throughout the profile and current
artwork. It remains a Final Year Project under development. No statistics,
employment, qualifications, finished features, or live demos were invented.

## Review and validation

Both primary compositions are rendered individually and in the complete local
GFM preview. Checks cover themes, desktop/laptop/phone widths, the responsive
boundary, source integrity, portrait proportions and bounds, SVG text bounds,
image decoding, overflow, default metrics visibility, the single collapsed text
equivalent, and the phone/WhatsApp pairing.

Seven viewport/theme cases pass: 1100px light/dark, 768px dark, 760px dark,
761px light, 390px dark, and 320px light. Images decode without errors; document
and expanded text layouts have no horizontal overflow; SVG text stays inside its
bounds; both major visuals align; the portrait keeps its proportions; metrics
and the phone number remain visible. The opening has exactly two visuals and
zero standalone visible descriptive paragraphs. The text equivalent works with
images hidden. Portrait layouts stay capped at 480px on tablets.

Visual refinement gives mobile Vantage additional space between its stack and
development status. Both project arrangements retain the same content. The
portrait face and hand remain clear of typography.

Local preview CSS approximates GitHub. The production sanitizer, profile layout,
image cache, and Actions permissions have not been exercised with unpublished
changes. No production GitHub-rendering verification is claimed.

## Local review and rebuild

Windows Command Prompt:

```cmd
cd /d D:\github\thonedra-dev
start "" ".preview\index.html"
```

Use Light/Dark controls and narrow the window. The ignored `.preview/` directory
contains current screenshots, SVG render inputs, and JSON verification results.

Checked-in assets display without a build or external image service. To rebuild,
Python 3, Node.js (tested with 22.14), and resvg are required. Existing temporary
rendering tools are reused:

```cmd
python tools\build_assets.py
python tools\validate_profile.py
git diff --check
```

On a fresh machine, install the rasterizer outside the repository:

```cmd
npm install --prefix "%TEMP%\architect-profile-render" --no-audit --no-fund --ignore-scripts @resvg/resvg-js
python tools\build_assets.py --render-tools "%TEMP%\architect-profile-render"
```

The published README requires no runtime or npm dependency. Pull request creation
and merging remain with the user.
