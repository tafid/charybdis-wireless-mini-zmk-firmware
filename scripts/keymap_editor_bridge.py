#!/usr/bin/env python3
import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent

KEYMAP = ROOT / "config/keymap/qwerty.keymap"
COMBOS = ROOT / "config/keymap/combos.dtsi"
MACROS = ROOT / "config/keymap/macros.dtsi"
BEHAVIORS = ROOT / "config/keymap/behaviors.dtsi"

OUT = ROOT / "firmwares/editor.keymap"


MARKERS = {
    "behaviors": ("// BEGIN_BEHAVIORS", "// END_BEHAVIORS"),
    "macros": ("// BEGIN_MACROS", "// END_MACROS"),
    "combos": ("// BEGIN_COMBOS", "// END_COMBOS"),
    "keymap": ("// BEGIN_KEYMAP", "// END_KEYMAP"),
}


def read(p):
    return p.read_text()


def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data)


def extract_section(text, start, end):
    pattern = re.compile(
        re.escape(start) + r"(.*?)" + re.escape(end),
        re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def replace_section(text, start, end, new_content):
    pattern = re.compile(
        re.escape(start) + r"(.*?)" + re.escape(end),
        re.DOTALL,
    )
    return pattern.sub(f"{start}\n{new_content}\n{end}", text)


# --------------------------
# FLATTEN
# --------------------------

def flatten():
    keymap = read(KEYMAP)
    combos = read(COMBOS)
    macros = read(MACROS)
    behaviors = read(BEHAVIORS)

    output = f"""
/* AUTO-GENERATED FILE — EDIT IN KEYMAP EDITOR */

{MARKERS["behaviors"][0]}
{behaviors}
{MARKERS["behaviors"][1]}

{MARKERS["macros"][0]}
{macros}
{MARKERS["macros"][1]}

{MARKERS["combos"][0]}
{combos}
{MARKERS["combos"][1]}

{MARKERS["keymap"][0]}
{keymap}
{MARKERS["keymap"][1]}
"""

    write(OUT, output.strip())
    print(f"[OK] Flattened → {OUT}")


# --------------------------
# SYNC BACK
# --------------------------

def sync():
    text = read(OUT)

    behaviors = extract_section(text, *MARKERS["behaviors"])
    macros = extract_section(text, *MARKERS["macros"])
    combos = extract_section(text, *MARKERS["combos"])
    keymap = extract_section(text, *MARKERS["keymap"])

    if not all([behaviors, macros, combos, keymap]):
        print("[ERROR] Missing markers or corrupted file")
        sys.exit(1)

    write(BEHAVIORS, behaviors + "\n")
    write(MACROS, macros + "\n")
    write(COMBOS, combos + "\n")
    write(KEYMAP, keymap + "\n")

    print("[OK] Synced back to repo")


# --------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: flatten | sync")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "flatten":
        flatten()
    elif cmd == "sync":
        sync()
    else:
        print("Unknown command")
