"""Dress up pygbag's generated page with the Pigeon Courier loading screen.

Runs in GitHub Actions after `pygbag --build`:
  - cream page background instead of gray
  - "Tap the pigeon to start" instead of "Ready to start ! Please click/touch page"
  - a cream loading screen with the pigeon flying a figure-eight, which steps aside once the game starts
"""
import shutil
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
web = repo / "build" / "web"
index = web / "index.html"
html = index.read_text(encoding="utf-8")

swaps = [
    ('"Ready to start ! Please click/touch page"', '"Tap the pigeon to start"'),
    ('platform.document.body.style.background = "#7f7f7f"', 'platform.document.body.style.background = "#f5ebd7"'),
    ("background-color:powderblue;", "background-color:#f5ebd7;"),
]
for old, new in swaps:
    if old in html:
        html = html.replace(old, new)
    else:
        print(f"note: did not find {old!r} (pygbag template may have changed)")

loader = (Path(__file__).parent / "loader.html").read_text(encoding="utf-8")
if "</body>" not in html:
    sys.exit("could not find </body> in index.html")
html = html.replace("</body>", loader + "\n</body>", 1)
index.write_text(html, encoding="utf-8")

frames = web / "loader"
frames.mkdir(exist_ok=True)
for name in ("pigeon_fly_1.png", "pigeon_fly_2.png", "pigeon_fly_3.png"):
    shutil.copy(repo / name, frames / name)

print("Loading screen added to", index)
