#!/usr/bin/env python3
"""Recover the numbers plotted in the paper's published figure panels from their vector EPS files.

Inputs   paper/*.eps   (MATLAB R2018a vector export, treated as data and never executed)
Outputs  numerics/figures/published_data.csv                long table: one row per plotted vertex
         numerics/figures/published_data_calibration.json   how each panel was calibrated, with checks

Usage    python numerics/figures/extract_published_data.py           regenerate both outputs
                                                                     (byte-identical every run)
         python numerics/figures/extract_published_data.py --check   same, then print the acceptance
                                                                     checks (expected theta grids, and
                                                                     Figure B.1 against the MATLAB values)
         python numerics/figures/extract_published_data.py --out-dir DIR   write both outputs to DIR

Dependencies: Python standard library only.  No Ghostscript, no network, no font files.

How it works (nothing about a panel is hard-coded except which file is which panel)
  1. PARSE.  A small PostScript interpreter runs the page body and records every painted object
     (fill, stroke, text string) with its path, colour, line width and dash pattern.  An operator
     it does not know raises an error, so nothing is skipped silently.
  2. CLASSIFY.  Every painted object must receive exactly one role: page/axes/legend background,
     axis line, tick mark, tick label, title glyph, data polyline, legend sample, legend glyph,
     legend border (or grid line, which the published panels do not have).  An object that fits no role
     raises an error, e.g. a filled marker.
  3. CALIBRATE.  Each axis map  data = intercept + slope * ps  is a least-squares line through its
     tick marks (position from the tick-mark path, value from the tick-label text).  See the note
     on single precision below.
  4. LABEL.  A data polyline gets the label of the legend entry whose sample line has the same
     colour, dash pattern and width.  Legend and axis-title text is drawn as glyph outlines (MATLAB
     LaTeX interpreter), not as character strings, so it is decoded with a glyph-outline codebook
     (GLYPHS below).  If a legend label cannot be decoded the series is named
     "unresolved (<colour>, <dash>)" instead.
  5. CONVERT.  Polyline vertices are mapped to (theta, value) and written out.

All arithmetic on coordinates uses exact rationals (fractions.Fraction), so the outputs do not depend
on platform, BLAS or floating-point summation order.

Coordinate frame ("ps" everywhere below): the frame of the page body as written in the file, i.e.
after the page-setup matrix [1 0 0 -1 0 H]: unit = PostScript point, x to the right, y DOWNWARDS from
the top edge of the bounding box.  Default user space is recovered by y_user = H - y.

Single precision (verified from the files, see "tick_fit" in the JSON)
  MATLAB converts data coordinates to IEEE single precision before placing them on the page.  Tick
  marks therefore sit at the position of single(tick value), not of the decimal label: in pibG.eps the
  ten y ticks fit a straight line to 0.0004 points (the rounding of the stored coordinates) if the
  targets are single(label), but only to 0.0097 points if they are the exact decimals.  The calibration
  targets are therefore single(label), and an extracted value estimates single(plotted value).  Two
  error sources follow:
    * the EPS stores coordinates with 3 decimals      -> "value_per_ps_digit" (one last-digit step)
    * the plotted double was rounded to single         -> "single_precision_ulp" (one ulp at the data)
  so |extracted - true double| <= about 0.5 digit + 0.5 ulp, and |extracted - single(true)| <= about
  0.5 digit.

Decimal rounding of the plotted numbers ("decimal_rounding" in the JSON, see decimal_rounding_test)
  A panel is flagged when every plotted value coincides, within the rounding of the stored coordinates,
  with single(a number that has only k decimals) and chance can be excluded.  Such a panel was drawn
  from numbers given to k decimals. They are listed as "value_rounded" next to the extracted values.
  The CSV always holds the extracted values, never the rounded ones.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import re
import struct
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

# --------------------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = REPO_ROOT / "paper"
OUT_DIR = REPO_ROOT / "numerics" / "figures"
CSV_NAME, JSON_NAME = "published_data.csv", "published_data_calibration.json"
OUT_CSV, OUT_JSON = OUT_DIR / CSV_NAME, OUT_DIR / JSON_NAME
REFERENCE_B1_CSV = REPO_ROOT / "numerics" / "matlab" / "Figure2_MATLAB" / "Figure2_reference.csv"

# (figure, panel, file).  The panel order is the \includegraphics order of fig:compare in
# paper/Manuscript.tex (Figure 1) and of fig:general in paper/OnlineAppendix.tex (B.1).
PANELS = [
    ("1", "a", "figure1.eps"),
    ("1", "b", "figure2.eps"),
    ("1", "c", "figure3.eps"),
    ("1", "d", "figure4.eps"),
    ("B.1", "a", "yaG.eps"),
    ("B.1", "b", "ybG.eps"),
    ("B.1", "c", "piaG.eps"),
    ("B.1", "d", "pibG.eps"),
]

CSV_COLUMNS = ["figure", "panel", "file", "series", "color", "dash", "point", "theta", "value"]

# ---- Tolerances (ps units unless stated otherwise)
# An axis line lies within this distance of the corresponding edge of the axes-background rectangle.
EDGE_TOL = Fraction(1)
# |tick-label anchor - tick-mark position|: the same number, stored with 5 and with 3 decimals.
TICK_LABEL_TOL = Fraction(1, 1000)
# Largest accepted residual of the tick fit (10 times the rounding of a stored coordinate).
TICK_FIT_TOL = Fraction(1, 200)
# |legend-text anchor y - legend-sample y|.
LEGEND_ROW_TOL = Fraction(1, 1000)
# Gap between neighbouring glyph boxes, in em, above which a word space is read.
# Observed in the eight files: 0.01-0.14 em inside words, 0.38-0.42 em between words.
SPACE_GAP_EM = 0.25
# |width/height of an outline - width/height in the codebook| for a glyph match.
GLYPH_ASPECT_TOL = 0.01
# Relative spread of the font sizes implied by the glyphs of one string.
GLYPH_SIZE_TOL = 0.01

# ---- Decimal-rounding test (see decimal_rounding_test)
# k = 0 .. ROUNDING_MAX_DECIMALS decimals are tried.
ROUNDING_MAX_DECIMALS = 6
# Allowed |value - single(k-decimal number)| in ps digits (coordinate rounding alone gives up to 0.5).
ROUNDING_TOL_DIGITS = Fraction(3, 4)
# Largest accepted probability that the coincidence is accidental.
ROUNDING_MAX_CHANCE = 1e-6

# Only used by --check: the theta grids the published curves are expected to be sampled on.
EXPECTED_THETA = {
    "1": ["0.01", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.99"],
    "B.1": ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"],
}

# Glyph-outline codebook.
#   key    path operators of the outline, one letter per segment (M moveto, L lineto, Q quadratic
#          curve), contours separated by "|", exactly as MATLAB R2018a wrote them
#   value  (character, width, height): control-point bounding box of that glyph in em units
# A glyph is accepted only if the operator string matches AND its width/height ratio agrees. The height
# then gives the font size, which must agree across the glyphs of a string (a mislabelled entry would
# break that: e.g. "S" and "N" differ by 6% in height).
# Provenance: the identities were established outside this script by comparing every outline with all
# glyphs of the seven BaKoMa TrueType Computer Modern fonts that ship with matplotlib (cmr10.ttf and, for
# theta, cmmi10.ttf turned out to be the sources).  Method: fontTools outline -> M/L/Q segments, y flipped,
# scaled to the same bounding-box height, 8 samples per segment, symmetric Hausdorff distance.  Each
# outline coincides with the named glyph within 0.0006 em. The next-best glyph is at least 0.02 em away,
# except for the apostrophe, whose design the cmmi10 comma shares (0.005 em) - the glyph sits 0.4-0.7 em
# above the baseline in "A's", so it is the apostrophe.  Widths and heights below are those of the font
# outlines.  The check needs fontTools and font files and is therefore not part of this script.
GLYPHS = {
    "MLQLQQQQQQQQQQLQQQQQQLQLQQLQLQQQQQQQQQQLQQQQQQQQQQLQLQ": ("S", 0.4429, 0.7271),
    "MQQQQQQQQQQQQQQQQQQQQQQQQLQQLQQ": ("c", 0.3818, 0.4595),
    "MQQQQQQQQQQQLLQQQQQQQLQQQ|MLQQQQQ": ("e", 0.3872, 0.4595),
    "MLQQLQQQLLLQQQQLQQLLLQQLQQQQLQQLL": ("n", 0.5073, 0.4419),
    "MQQQLQQQQQQQQQQQQQQQLQQQQLLLQQQQQQQQQQ|MQQQQQLQQQ": ("a", 0.4531, 0.4595),
    "MLQQLQQQLLLQQQQQQQQQLQQQLQLL": ("r", 0.3379, 0.4419),
    "MLQQLQQLLLQQLL|MQQQQQQQQQ": ("i", 0.2183, 0.6689),
    "MQQQQQQQQQQQQQ|MQQQQQQQQQQQQQQ": ("o", 0.4434, 0.4595),
    "MLQLQLLQLLQLLLQLQQLQLLQLL": ("N", 0.6870, 0.6831),
    "MQQQQLQLLLQQLQQQQQQQQQQQQQQQLQLQQLQLQQQQQQQQQQ": ("G", 0.6787, 0.7271),
    "MQQQQQQQQQQQQ|MQQQQQQQQQQQQQ": ("0", 0.4209, 0.6880),
    "MLQQQLLLQQQQQLQQQLLLQQQLLLQQQQ": ("u", 0.5073, 0.4531),
    "MLQQQLLLQQQQQQQQQQQQLL|MQQQQQQQQQQQL": ("b", 0.4961, 0.7051),
    "MLQLQQQQQQLQQQQQQQLQLQQLQLQQQQQQQLQQQQQQQQLQLQ": ("s", 0.3267, 0.4595),
    "MLLLQQLLLLLLQQQQLLLQQQQQ": ("t", 0.3130, 0.6265),
    "MLQLQLLQQQQQQQQLQQQQQQLQQQQQQLQQLLQLL|MLQQQQLQQQL": ("R", 0.6987, 0.7051),
    "MLQQLQQQLLLQQLL": ("l", 0.2261, 0.6938),
    "MLQLQLQLQQLLLQLLLLQQQLL|MLLL": ("A", 0.6846, 0.7158),
    "MLQLQLLQQQQQQQQQQQL|MQQLQQQQQQLL|MLQQQQQQQQLQQQL": ("B", 0.6167, 0.6831),
    "MQQQQQQQQQQQQQQQQQ": ("'", 0.1240, 0.3037),  # cmr10 quoteright, written here as ASCII apostrophe
    "MLQLQLLQQQQQQLLQLL|MLQQQQQLQQQL": ("P", 0.5908, 0.6831),
    "MLQQLLLLLQQQQQQQQQQQQQQQQQLLLLQQLLLQQLQQQLLQQLL": ("fi", 0.5029, 0.7051),  # the fi ligature
    "MQQQQQQQQQQQQQQ|MQQQQQQQQQQQQQQQQQ": ("O", 0.6650, 0.7271),
    "MQQQQQQQQLQQQLLLQQQLLLQQ|MQQQQLQQQQQQQQ": ("d", 0.4956, 0.7051),
    "MQQQQQQQQQQQQQQQQQQQQQQQQQQQQ|MQQQQQQQ|MQQQQQQQQQQQQQQQQQQQQ": ("Q", 0.6709, 0.8989),
    "MQQLLQQLLLQQLLQQQQLLLQQLQQQQQQQQQQQQ": ("y", 0.4888, 0.6362),
    "MQQQLQQQQQQQLQQQQQQQQQQL|MQQQQLQQQ|MLQQQQQQ": ("\u03b8", 0.4170, 0.7163),  # cmmi10 theta, U+03B8
}

COLOR_NAMES = {(1, 0, 0): "red", (0, 0, 1): "blue", (0, 0, 0): "black", (0, 1, 0): "green",
               (1, 0, 1): "magenta", (0, 1, 1): "cyan", (1, 1, 0): "yellow", (1, 1, 1): "white"}


class EpsError(RuntimeError):
    """The file does not have the structure this script understands (never guessed around)."""


# --------------------------------------------------------------------------------------------------
# 1. PostScript subset: tokenizer and interpreter
# --------------------------------------------------------------------------------------------------

_TOKEN = re.compile(
    r"""(?P<space>\s+)
      | (?P<comment>%[^\r\n]*)
      | \((?P<string>(?:\\.|[^\\()])*)\)          # (text), nested parentheses do not occur
      | (?P<delim>[\[\]{}])
      | /(?P<literal>[^\s\[\]{}()<>/%]*)          # /name
      | (?P<word>[^\s\[\]{}()<>/%]+)              # number or operator
    """,
    re.X,
)
_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?\Z")


class Name(str):
    """A literal name such as /Helvetica."""


class String(str):
    """A string such as (0.2)."""


class Proc(list):
    """A procedure body { ... } kept as a token list."""


def tokenize(text: str) -> list:
    """Split PostScript source into (kind, value) tokens and fail on anything unexpected."""
    tokens, pos = [], 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if m is None:
            raise EpsError(f"cannot tokenize at offset {pos}: {text[pos:pos + 40]!r}")
        pos = m.end()
        kind, value = m.lastgroup, m.group(m.lastgroup)
        if kind in ("space", "comment"):
            continue
        if kind == "word" and _NUMBER.match(value):
            tokens.append(("number", Fraction(value)))  # Fraction("849.727") is exact
        else:
            tokens.append((kind, value))
    return tokens


IDENTITY = (Fraction(1), Fraction(0), Fraction(0), Fraction(1), Fraction(0), Fraction(0))


def matmul(m: tuple, n: tuple) -> tuple:
    """PostScript matrices [a b c d tx ty] act on row vectors. This returns "m, then n"."""
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * c2, a * b2 + b * d2, c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2)


def transform(m: tuple, x, y) -> tuple:
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def decimals_of(x: Fraction) -> int:
    """Number of digits after the decimal point needed to write x exactly."""
    k = 0
    while (x * 10 ** k).denominator != 1:
        k += 1
    return k


@dataclass
class Subpath:
    ops: str = ""                                # one letter per segment: M, L or Q
    pts: list = field(default_factory=list)      # points in the page frame (Q adds control point + end point)
    local: list = field(default_factory=list)    # the same points before the CTM (upright glyph shapes)
    closed: bool = False


@dataclass
class Painted:
    kind: str                # "fill", "stroke" or "text"
    order: int               # index in drawing order
    ctm: tuple               # current transformation matrix when painted
    rgb: tuple
    line_width: Fraction
    dash: tuple              # (dash array, offset), empty array = solid
    subpaths: list = field(default_factory=list)
    text: str = ""           # text objects only: the string shown
    anchor: tuple = ()       # text objects only: origin of the text frame in the page frame
    role: str = ""           # assigned by classify()


PROCSET = "procset (Apache XML Graphics Std ProcSet) 1.2 0"


class Interpreter:
    """Runs the page body.  Operator names are the aliases defined by the prolog PROCSET, which
    read_eps() requires every file to carry:
    GS gsave, GR grestore, CT concat, N newpath, M moveto, L lineto, QT quadratic curveto,
    cp closepath, re rectangle, f fill, S stroke, GC setgray, RC setrgbcolor, LW setlinewidth,
    LJ setlinejoin, ML setmiterlimit, F select font, t show."""

    def __init__(self) -> None:
        self.stack: list = []
        self.procs: dict = {}        # procedures defined in the body (MATLAB stores repeated glyphs this way)
        self.saved: list = []        # gsave stack
        self.painted: list = []
        self.coordinate_decimals = 0  # most decimals seen in any path coordinate of the file
        self.gs = {"ctm": IDENTITY, "rgb": (Fraction(0),) * 3, "lw": Fraction(1),
                   "dash": ((), Fraction(0)), "path": []}

    # ---- operand stack helpers
    def pop(self, kind):
        if not self.stack or not isinstance(self.stack[-1], kind):
            raise EpsError(f"expected {kind.__name__} on the operand stack, found {self.stack[-1:]!r}")
        return self.stack.pop()

    def numbers(self, count: int) -> list:
        values = [self.pop(Fraction) for _ in range(count)]
        return values[::-1]

    def path_numbers(self, count: int) -> list:
        values = self.numbers(count)
        self.coordinate_decimals = max([self.coordinate_decimals] + [decimals_of(v) for v in values])
        return values

    # ---- execution
    def run(self, tokens: list) -> None:
        i = 0
        while i < len(tokens):
            kind, value = tokens[i]
            if kind == "number":
                self.stack.append(value)
            elif kind == "string":
                self.stack.append(String(value))
            elif kind == "literal":
                self.stack.append(Name(value))
            elif kind == "delim" and value == "[":      # array of numbers, e.g. a matrix or dash array
                j = i + 1
                while tokens[j] != ("delim", "]"):
                    if tokens[j][0] != "number":
                        raise EpsError(f"non-numeric array element {tokens[j]!r}")
                    j += 1
                self.stack.append(tuple(t[1] for t in tokens[i + 1:j]))
                i = j
            elif kind == "delim" and value == "{":      # procedure body: store, do not execute
                depth, j = 1, i + 1
                while depth:
                    depth += {("delim", "{"): 1, ("delim", "}"): -1}.get(tokens[j], 0)
                    j += 1
                self.stack.append(Proc(tokens[i + 1:j - 1]))
                i = j - 1
            elif kind == "word":
                self.execute(value)
            else:
                raise EpsError(f"unexpected token {tokens[i]!r}")
            i += 1

    def add_segment(self, op: str, local_points: list) -> None:
        path = self.gs["path"]
        if op == "M":
            path.append(Subpath())
        elif not path:
            raise EpsError(f"path segment {op} without a current point")
        sub = path[-1]
        sub.ops += op
        sub.local += local_points
        sub.pts += [transform(self.gs["ctm"], x, y) for x, y in local_points]

    def paint(self, kind: str, **extra) -> None:
        g = self.gs
        self.painted.append(Painted(kind=kind, order=len(self.painted), ctm=g["ctm"], rgb=g["rgb"],
                                    line_width=g["lw"], dash=g["dash"], **extra))

    def execute(self, op: str) -> None:
        g = self.gs
        if op == "GS":
            self.saved.append(copy.deepcopy(g))
        elif op == "GR":
            self.gs = self.saved.pop()
        elif op == "CT":
            g["ctm"] = matmul(self.pop(tuple), g["ctm"])
        elif op == "scale":
            sx, sy = self.numbers(2)
            g["ctm"] = matmul((sx, Fraction(0), Fraction(0), sy, Fraction(0), Fraction(0)), g["ctm"])
        elif op == "GC":
            g["rgb"] = tuple(self.numbers(1)) * 3
        elif op == "RC":
            g["rgb"] = tuple(self.numbers(3))
        elif op == "LW":
            (g["lw"],) = self.numbers(1)
        elif op in ("LJ", "ML", "setlinecap"):          # join / miter limit / cap: irrelevant here
            self.numbers(1)
        elif op == "setdash":
            (offset,) = self.numbers(1)
            g["dash"] = (self.pop(tuple), offset)
        elif op == "N":
            g["path"] = []
        elif op in ("M", "moveto"):
            x, y = self.path_numbers(2)
            self.add_segment("M", [(x, y)])
        elif op == "L":
            x, y = self.path_numbers(2)
            self.add_segment("L", [(x, y)])
        elif op == "QT":                                 # quadratic Bezier: control point, end point
            x1, y1, x2, y2 = self.path_numbers(4)
            self.add_segment("Q", [(x1, y1), (x2, y2)])
        elif op == "cp":
            if not g["path"]:
                raise EpsError("closepath without a current path")
            g["path"][-1].closed = True
        elif op == "re":                                # x y w h re: closed rectangle (see prolog)
            x, y, w, h = self.path_numbers(4)
            self.add_segment("M", [(x, y)])
            for corner in ((x + w, y), (x + w, y + h), (x, y + h)):
                self.add_segment("L", [corner])
            g["path"][-1].closed = True
        elif op in ("f", "S"):
            self.paint("fill" if op == "f" else "stroke", subpaths=g["path"])
            g["path"] = []
        elif op == "F":                                  # /Font size F: the font is not needed
            self.numbers(1)
            self.pop(Name)
        elif op == "t":                                  # show a string and keep where its frame sits
            self.paint("text", text=str(self.pop(String)),
                       anchor=transform(g["ctm"], Fraction(0), Fraction(0)))
        elif op == "def":
            body = self.pop(Proc)
            self.procs[str(self.pop(Name))] = body
        elif op in self.procs:
            self.run(self.procs[op])
        else:
            raise EpsError(f"unsupported PostScript operator {op!r}")


def read_eps(path: Path) -> dict:
    """Parse one EPS file into header fields and the list of painted objects (page frame)."""
    text = path.read_bytes().decode("latin-1")

    def header(key: str) -> str:
        m = re.search(rf"^%%{key}:[ \t]*(.*?)[ \t\r]*$", text, re.M)
        if m is None:
            raise EpsError(f"{path.name}: missing %%{key}")
        return m.group(1)

    bbox = [Fraction(v) for v in header("BoundingBox").split()]
    setup = re.search(r"%%BeginPageSetup(.*?)%%EndPageSetup", text, re.S)
    trailer = text.find("%%Trailer")
    if setup is None or trailer < 0:
        raise EpsError(f"{path.name}: page setup or trailer not found")
    if PROCSET not in text[:setup.start()]:
        raise EpsError(f"{path.name}: prolog is not the expected {PROCSET}")

    # The page setup must be the plain flip [1 0 0 -1 0 H] that defines the page frame used here.
    setup_tokens = tokenize(setup.group(1))
    matrix = tuple(t[1] for t in setup_tokens[1:-2])
    height = bbox[3] - bbox[1]
    if (setup_tokens[0] != ("delim", "[") or setup_tokens[-2:] != [("delim", "]"), ("word", "CT")]
            or matrix != (1, 0, 0, -1, 0, height) or bbox[:2] != [0, 0]):
        raise EpsError(f"{path.name}: unexpected page setup {setup.group(1).strip()!r}")

    interp = Interpreter()
    interp.run(tokenize(text[setup.end():trailer]))
    if interp.stack or interp.saved:
        raise EpsError(f"{path.name}: unbalanced operand or graphics-state stack")
    return {
        "creator": header("Creator").strip("()").replace("\\(", "(").replace("\\)", ")"),
        "creation_date": header("CreationDate"),
        "bbox": bbox,
        "page_setup_matrix": matrix,
        "coordinate_decimals": interp.coordinate_decimals,
        "painted": interp.painted,
    }


# --------------------------------------------------------------------------------------------------
# 2. Geometry helpers and classification of the painted objects
# --------------------------------------------------------------------------------------------------

def polyline(o: Painted):
    """Vertices if the path is a single subpath of straight segments, else None."""
    if len(o.subpaths) != 1 or set(o.subpaths[0].ops) - {"M", "L"}:
        return None
    return o.subpaths[0].pts


def rectangle(o: Painted):
    """(x_min, y_min, x_max, y_max) if the path is one closed axis-aligned rectangle, else None."""
    pts = polyline(o)
    if pts is None or len(pts) != 4 or not o.subpaths[0].closed:
        return None
    xs, ys = sorted({p[0] for p in pts}), sorted({p[1] for p in pts})
    if len(xs) != 2 or len(ys) != 2 or {(x, y) for x in xs for y in ys} != set(pts):
        return None
    return (xs[0], ys[0], xs[1], ys[1])


def segment(o: Painted):
    """(p1, p2) if the path is a single open straight segment, else None."""
    pts = polyline(o)
    if pts is None or len(pts) != 2 or o.subpaths[0].closed:
        return None
    return pts[0], pts[1]


def bounds(objects: list) -> tuple:
    xs = [p[0] for o in objects for sp in o.subpaths for p in sp.pts]
    ys = [p[1] for o in objects for sp in o.subpaths for p in sp.pts]
    return (min(xs), min(ys), max(xs), max(ys))


def inside(box: tuple, outer: tuple, tol=Fraction(0)) -> bool:
    return (box[0] >= outer[0] - tol and box[1] >= outer[1] - tol
            and box[2] <= outer[2] + tol and box[3] <= outer[3] + tol)


def style(o: Painted) -> tuple:
    """What identifies a line style: colour, dash pattern, width."""
    return (o.rgb, o.dash, o.line_width)


def color_name(rgb: tuple) -> str:
    key = tuple(int(c) if c.denominator == 1 else None for c in rgb)
    return COLOR_NAMES.get(key, "#" + "".join(f"{round(float(c) * 255):02x}" for c in rgb))


def dash_name(o: Painted) -> str:
    array = o.dash[0]
    if not array:
        return "solid"
    if len(array) == 2:   # one on/off pair: dots if the "on" piece is about as long as the line is wide
        return "dotted" if array[0] <= Fraction(3, 2) * o.line_width else "dashed"
    if len(array) == 4:
        return "dash-dot"
    return "dash[" + " ".join(str(float(a)) for a in array) + "]"


def decode_glyph_string(glyphs: list) -> dict:
    """Decode fills that share one text frame into a string (reading order = local x)."""
    items = []
    for g in glyphs:
        xs = [float(p[0]) for sp in g.subpaths for p in sp.local]
        ys = [float(p[1]) for sp in g.subpaths for p in sp.local]
        width, height = max(xs) - min(xs), max(ys) - min(ys)
        entry = GLYPHS.get("|".join(sp.ops for sp in g.subpaths))
        if entry and height > 0 and abs(width / height - entry[1] / entry[2]) <= GLYPH_ASPECT_TOL:
            items.append((min(xs), max(xs), entry[0], height / entry[2]))   # last item: implied font size
        else:
            items.append((min(xs), max(xs), "?", None))
    items.sort(key=lambda it: it[0])
    sizes = sorted(it[3] for it in items if it[3] is not None)
    if not sizes:
        return {"text": "?" * len(items), "decoded": False, "font_size": None, "gaps_em": []}
    em = sizes[len(sizes) // 2]                      # median font size of the string
    text, gaps = items[0][2], []
    for prev, cur in zip(items, items[1:]):
        gap = (cur[0] - prev[1]) / em               # white space between neighbouring glyph boxes
        gaps.append(gap)
        text += (" " if gap > SPACE_GAP_EM else "") + cur[2]
    return {
        "text": text,
        "decoded": "?" not in text and (sizes[-1] - sizes[0]) / em <= GLYPH_SIZE_TOL,
        "font_size": em,
        "size_spread": (sizes[-1] - sizes[0]) / em,
        "gaps_em": gaps,
    }


def classify(eps: dict, name: str) -> dict:
    """Give every painted object a role and return the scene description of one panel."""
    painted = eps["painted"]
    fills = [o for o in painted if o.kind == "fill"]
    strokes = [o for o in painted if o.kind == "stroke"]
    texts = [o for o in painted if o.kind == "text"]

    def fail(message: str):
        raise EpsError(f"{name}: {message}")

    # ---- rectangles: page background, legend frame (border + background), axes background
    page = (eps["bbox"][0], eps["bbox"][1], eps["bbox"][2], eps["bbox"][3])
    for o in fills:
        if rectangle(o) == page:
            o.role = "page_background"
    borders = [o for o in strokes if rectangle(o)]
    if len(borders) > 1:
        fail("more than one stroked rectangle (expected at most the legend border)")
    legend_box = rectangle(borders[0]) if borders else None
    legend_background = None
    axes_background = None
    for o in fills:
        box = rectangle(o)
        if box is None or o.role:
            continue
        if legend_box is not None and box == legend_box and legend_background is None:
            legend_background, o.role = o, "legend_background"
        elif axes_background is None:
            axes_background, o.role = o, "axes_background"
        else:
            fail("unexpected extra filled rectangle")
    if axes_background is None:
        fail("axes background rectangle not found")
    if borders:
        if legend_background is None:
            fail("legend border without legend background")
        borders[0].role = "legend_border"
    # page frame: y grows downwards, so the smaller y is the TOP edge of the axes
    x_left, y_top, x_right, y_bottom = rectangle(axes_background)

    # ---- axis lines: straight strokes spanning the axes box along one of its edges
    def near(a, b) -> bool:
        return abs(a - b) <= EDGE_TOL

    def spanning(o: Painted):
        """("h", y) or ("v", x) if o is a straight segment right across the axes box, else None."""
        seg = segment(o)
        if seg is not None:
            (x1, y1), (x2, y2) = sorted(seg)
            if y1 == y2 and near(x1, x_left) and near(x2, x_right):
                return ("h", y1)
            if x1 == x2 and near(y1, y_top) and near(y2, y_bottom):
                return ("v", x1)
        return None

    axis_lines = {}
    for o in strokes:
        direction, position = spanning(o) or (None, None)
        side = None
        if direction == "h":
            side = "bottom" if near(position, y_bottom) else "top" if near(position, y_top) else None
        elif direction == "v":
            side = "left" if near(position, x_left) else "right" if near(position, x_right) else None
        if side:
            if side in axis_lines:
                fail(f"two candidates for the {side} axis line")
            axis_lines[side], o.role = o, "axis_line"
    if "bottom" not in axis_lines or "left" not in axis_lines:
        fail("bottom or left axis line not found")
    line_pos = {side: (segment(o)[0][1] if side in ("bottom", "top") else segment(o)[0][0])
                for side, o in axis_lines.items()}
    furniture = style(axis_lines["bottom"])
    if any(style(o) != furniture for o in axis_lines.values()):
        fail("axis lines do not share one line style")

    # ---- tick marks: short strokes in the axis style, perpendicular to and starting on an axis line
    ticks = {side: [] for side in axis_lines}
    for o in strokes:
        seg = segment(o)
        if o.role or seg is None or style(o) != furniture:
            continue
        (x1, y1), (x2, y2) = seg
        for side in axis_lines:
            if side in ("bottom", "top") and x1 == x2 and line_pos[side] in (y1, y2):
                ticks[side].append(x1)
                o.role = "tick_mark"
            elif side in ("left", "right") and y1 == y2 and line_pos[side] in (x1, x2):
                ticks[side].append(y1)
                o.role = "tick_mark"
    for side, mirror in (("bottom", "top"), ("left", "right")):
        if mirror in ticks and sorted(ticks[mirror]) != sorted(ticks[side]):
            fail(f"tick marks on the {mirror} side do not mirror those on the {side} side")
    tick_pos = {"x": sorted(ticks["bottom"]), "y": sorted(ticks["left"])}

    # ---- tick labels: each text string must sit on exactly one tick.  Its frame origin ("anchor")
    #      carries the tick coordinate: x labels are anchored below the axis at the tick's x,
    #      y labels to the left of the axis at the tick's y.
    tick_label = {"x": {}, "y": {}}
    anchor_offset = Fraction(0)
    for o in texts:
        ax, ay = o.anchor
        hits = []
        if ay > line_pos["bottom"]:
            hits += [("x", t, abs(ax - t)) for t in tick_pos["x"] if abs(ax - t) <= TICK_LABEL_TOL]
        if ax < line_pos["left"]:
            hits += [("y", t, abs(ay - t)) for t in tick_pos["y"] if abs(ay - t) <= TICK_LABEL_TOL]
        if len(hits) != 1 or hits[0][1] in tick_label[hits[0][0]]:
            fail(f"text {o.text!r} cannot be assigned to exactly one tick mark")
        if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", o.text):
            fail(f"tick label {o.text!r} is not a plain decimal number")
        axis, position, offset = hits[0]
        tick_label[axis][position] = o
        anchor_offset = max(anchor_offset, offset)
        o.role = "tick_label"
    for axis in "xy":
        if len(tick_label[axis]) < 2:
            fail(f"fewer than two labelled ticks on the {axis} axis")

    # ---- remaining strokes.  Legend samples: straight segments inside the legend frame, drawn after its
    #      background.  Grid lines: lines right across the axes box that have no legend entry of the
    #      same style (none occur in the eight published panels).  Everything else must be a data
    #      polyline drawn before the legend.
    samples = [o for o in strokes if not o.role and legend_box is not None and segment(o)
               and o.order > legend_background.order and inside(bounds([o]), legend_box)]
    for o in samples:
        o.role = "legend_sample"
    curves = []
    for o in strokes:
        if o.role:
            continue
        if spanning(o) and style(o) not in {style(s) for s in samples}:
            o.role = "grid_line"
            continue
        pts = polyline(o)
        if (pts is None or len(pts) < 2 or o.subpaths[0].closed or style(o) == furniture
                or (legend_background is not None and o.order > legend_background.order)
                or not inside(bounds([o]), (x_left, y_top, x_right, y_bottom), EDGE_TOL)):
            fail(f"stroked object #{o.order} is neither axis furniture, legend sample nor data polyline")
        if any(b[0] <= a[0] for a, b in zip(pts, pts[1:])):
            fail(f"data polyline #{o.order} is not ordered by increasing x")
        o.role = "data_polyline"
        curves.append(o)
    if not curves:
        fail("no data polyline found")

    # ---- remaining fills are glyph outlines, and fills sharing one text frame (CTM) form one string
    frames: dict = {}
    for o in fills:
        if not o.role:
            frames.setdefault(o.ctm, []).append(o)
    titles = {}
    legend_texts = []
    for ctm, glyphs in frames.items():
        box = bounds(glyphs)
        decoded = decode_glyph_string(glyphs)
        decoded["anchor"] = transform(ctm, Fraction(0), Fraction(0))
        upright = ctm[1] == 0 and ctm[2] == 0
        if (legend_box is not None and inside(box, legend_box)
                and all(g.order > legend_background.order for g in glyphs)):
            role = "legend_glyph"
            legend_texts.append(decoded)
        elif upright and box[1] > y_bottom and "x" not in titles:       # below the axes
            role, titles["x"] = "title_glyph", decoded
        elif not upright and box[2] < x_left and "y" not in titles:     # left of the axes, rotated
            role, titles["y"] = "title_glyph", decoded
        else:
            fail(f"filled shapes at {tuple(float(v) for v in box)} are not legend or axis-title text "
                 "(markers?)")
        for g in glyphs:
            g.role = role

    # ---- legend entries: a sample line and the text whose frame origin lies on the same row
    entries = []
    row_offset = Fraction(0)
    for s in samples:
        (x1, y1), (x2, y2) = segment(s)
        rows = [t for t in legend_texts if abs(t["anchor"][1] - y1) <= LEGEND_ROW_TOL] if y1 == y2 else []
        if len(rows) != 1:
            fail(f"legend sample at y={float(y1)} has no unique text on its row")
        row_offset = max(row_offset, abs(rows[0]["anchor"][1] - y1))
        entries.append({"sample": s, "text": rows[0]})
    if len(entries) != len(legend_texts):
        fail("legend texts and legend sample lines do not pair up one-to-one")

    unassigned = [o.order for o in painted if not o.role]
    if unassigned:
        fail(f"painted objects without a role: {unassigned}")
    return {
        "axes_box": {"x_left": x_left, "x_right": x_right, "y_bottom": y_bottom, "y_top": y_top},
        "line_pos": line_pos, "tick_pos": tick_pos, "tick_label": tick_label, "titles": titles,
        "legend_box": legend_box, "entries": entries, "curves": curves,
        "anchor_offset": anchor_offset, "row_offset": row_offset,
    }


# --------------------------------------------------------------------------------------------------
# 3. Calibration
# --------------------------------------------------------------------------------------------------

def single(x: Fraction) -> Fraction:
    """x rounded to IEEE single precision (via double, as MATLAB's single(double) does), exactly."""
    return Fraction(struct.unpack("<f", struct.pack("<f", float(x)))[0])


def single_ulp(x: Fraction) -> float:
    """Spacing of single-precision numbers at |x|."""
    exponent = math.frexp(abs(float(x)))[1]          # |x| = m * 2**exponent with 0.5 <= m < 1
    return 2.0 ** (max(exponent, -125) - 24)


def fit_line(ps: list, targets: list) -> tuple:
    """Exact least-squares line  target = intercept + slope * ps  and its residuals."""
    n = len(ps)
    mean_p, mean_t = sum(ps) / n, sum(targets) / n
    slope = sum((p - mean_p) * (t - mean_t) for p, t in zip(ps, targets)) / sum((p - mean_p) ** 2 for p in ps)
    intercept = mean_t - slope * mean_p
    return intercept, slope, [intercept + slope * p - t for p, t in zip(ps, targets)]


def calibrate(scene: dict, axis: str, decimals: int, name: str) -> dict:
    """Linear map ps -> data for one axis from its labelled tick marks."""
    labelled = sorted(scene["tick_label"][axis].items())
    ps = [p for p, _ in labelled]
    labels = [o.text for _, o in labelled]
    exact = [Fraction(text) for text in labels]
    intercept, slope, residuals = fit_line(ps, [single(v) for v in exact])   # the calibration used
    _, _, residuals_decimal = fit_line(ps, exact)                            # diagnostic only
    if slope == 0:
        raise EpsError(f"{name}: degenerate {axis}-axis calibration")
    if max(abs(r) for r in residuals) > TICK_FIT_TOL * abs(slope):
        raise EpsError(f"{name}: {axis}-axis tick marks are not linear in their labels "
                       "(log axis or mislabelled tick?)")
    box = scene["axes_box"]
    edges = (box["x_left"], box["x_right"]) if axis == "x" else (box["y_bottom"], box["y_top"])
    return {
        "intercept": intercept, "slope": slope, "ps": ps, "labels": labels,
        "max_residual": max(abs(r) for r in residuals),
        "max_residual_decimal": max(abs(r) for r in residuals_decimal),
        "limits": [intercept + slope * e for e in edges],
        "per_digit": abs(slope) / 10 ** decimals,      # data units per last-digit step of a ps coordinate
        "unlabelled_ticks": [p for p in scene["tick_pos"][axis] if p not in scene["tick_label"][axis]],
    }


def decimal_rounding_test(values: list, per_digit: Fraction):
    """Were the plotted numbers given to only k decimals?  Returns a dict for the smallest such k, or None.

    For k = 0, 1, ... each distinct value v is compared with single(g), g = the nearest k-decimal number.
    Accepted if (i) the largest deviation D is within ROUNDING_TOL_DIGITS ps digits, i.e. explained by the
    rounding of the stored coordinate, and (ii) this is not a coincidence.  A plotted number unrelated to
    the k-decimal grid passes (i) only if it lies in a window of width ulp + 2 D around a grid point (ulp:
    every double in a single-precision cell is drawn at the same place), so for n distinct values
    P(all pass) <= ((ulp + 2 D) / 10**-k) ** n, which must not exceed ROUNDING_MAX_CHANCE.  Condition (ii)
    is what rejects grids finer than the resolution or than single precision."""
    distinct = sorted(set(values))
    ulp = Fraction(single_ulp(max(abs(v) for v in distinct)))
    for k in range(ROUNDING_MAX_DECIMALS + 1):
        step = Fraction(1, 10 ** k)
        deviation = max(abs(v - single(round(v / step) * step)) for v in distinct)
        chance = min(1.0, float((ulp + 2 * deviation) / step)) ** len(distinct)
        if deviation <= ROUNDING_TOL_DIGITS * per_digit and chance <= ROUNDING_MAX_CHANCE:
            return {"decimals": k, "n_distinct_values": len(distinct),
                    "max_abs_deviation_in_ps_digits": sig(deviation / per_digit, 3),
                    "chance_probability": sig(chance, 2)}
    return None


# --------------------------------------------------------------------------------------------------
# 4. Output formatting (exact, platform independent)
# --------------------------------------------------------------------------------------------------

def fixed(x: Fraction, decimals: int) -> str:
    """x as a fixed-point decimal string, rounded half-to-even with integer arithmetic."""
    n = round(x * 10 ** decimals)
    digits = str(abs(n)).rjust(decimals + 1, "0")
    body = digits[:-decimals] + "." + digits[-decimals:] if decimals else digits
    return ("-" if n < 0 else "") + body


def decimals_for(resolution: Fraction, guard: int) -> int:
    """Smallest d with 10**-d <= resolution, plus `guard` extra digits."""
    d = 0
    while Fraction(1, 10 ** d) > resolution:
        d += 1
    return d + guard


def sig(x, digits: int = 4) -> float:
    """Float rounded to a few significant digits (for diagnostics in the JSON)."""
    return float(f"{float(x):.{digits}g}")


def to_json(obj, level: int = 0) -> str:
    """JSON text with containers of plain scalars kept on one line (when short), others expanded."""
    if isinstance(obj, (dict, list)):
        flat = json.dumps(obj, ensure_ascii=False)
        scalars = all(not isinstance(v, (dict, list)) for v in (obj.values() if isinstance(obj, dict) else obj))
        if not obj or (scalars and len(flat) <= 110):
            return flat
        pad = "  " * (level + 1)
        if isinstance(obj, dict):
            parts = [f"{pad}{json.dumps(k, ensure_ascii=False)}: {to_json(v, level + 1)}"
                     for k, v in obj.items()]
            return "{\n" + ",\n".join(parts) + "\n" + "  " * level + "}"
        parts = [pad + to_json(v, level + 1) for v in obj]
        return "[\n" + ",\n".join(parts) + "\n" + "  " * level + "]"
    return json.dumps(obj, ensure_ascii=False)


# --------------------------------------------------------------------------------------------------
# 5. One panel: parse, classify, calibrate, label, convert
# --------------------------------------------------------------------------------------------------

def extract_panel(figure: str, panel: str, name: str) -> dict:
    eps = read_eps(FIGURE_DIR / name)
    scene = classify(eps, name)
    decimals = eps["coordinate_decimals"]
    cal = {axis: calibrate(scene, axis, decimals, name) for axis in "xy"}
    # Output precision.  theta: last printed digit is the first one not larger than the x resolution
    # (a further digit would only show single-precision noise such as single(0.99) = 0.99000001).
    # value: one guard digit beyond the y resolution, so printing adds < 5% of a ps digit.
    theta_decimals = decimals_for(cal["x"]["per_digit"], 0)
    value_decimals = decimals_for(cal["y"]["per_digit"], 1)

    # ---- legend entries and the style -> label lookup
    legend = []
    by_style: dict = {}
    for entry in scene["entries"]:
        sample, text = entry["sample"], entry["text"]
        by_style.setdefault(style(sample), []).append(text)
        legend.append({
            "label": text["text"], "decoded": text["decoded"],
            "color": color_name(sample.rgb), "dash": dash_name(sample),
            "dash_array_ps": [float(a) for a in sample.dash[0]], "line_width_ps": float(sample.line_width),
            "sample_line_ps": [[float(c) for c in p] for p in segment(sample)],
            "font_size_ps": sig(text["font_size"]) if text["font_size"] else None,
        })

    # ---- data polylines
    box = scene["axes_box"]
    series, rows = [], []
    for curve in scene["curves"]:
        matches = by_style.get(style(curve), [])
        if len(matches) == 1 and matches[0]["decoded"]:
            label, source = matches[0]["text"], "legend text of the entry with the same colour, dash and width"
        else:   # no legend, ambiguous style, or undecodable glyphs: do not guess a scenario name
            label = f"unresolved ({color_name(curve.rgb)}, {dash_name(curve)})"
            source = "UNRESOLVED: no unique decodable legend entry with this line style"
        pts = polyline(curve)
        theta = [cal["x"]["intercept"] + cal["x"]["slope"] * x for x, _ in pts]
        value = [cal["y"]["intercept"] + cal["y"]["slope"] * y for _, y in pts]
        for k, (t, v) in enumerate(zip(theta, value), start=1):
            rows.append({"figure": figure, "panel": panel, "file": name, "series": label,
                         "color": color_name(curve.rgb), "dash": dash_name(curve), "point": k,
                         "theta": fixed(t, theta_decimals), "value": fixed(v, value_decimals)})
        series.append({
            "label": label, "label_source": source,
            "color": color_name(curve.rgb), "rgb": [float(c) for c in curve.rgb], "dash": dash_name(curve),
            "dash_array_ps": [float(a) for a in curve.dash[0]], "line_width_ps": float(curve.line_width),
            "n_points": len(pts),
            "points_ps": [[float(x), float(y)] for x, y in pts],
            "theta": [float(fixed(t, theta_decimals)) for t in theta],
            "value": [float(fixed(v, value_decimals)) for v in value],
            # vertices lying exactly on the top/bottom edge of the axes would indicate clipping
            "n_vertices_on_top_or_bottom_edge": sum(1 for _, y in pts if y in (box["y_top"], box["y_bottom"])),
            "_exact": {"theta": theta, "value": value},     # removed before writing, used by --check
        })
    if len({s["label"] for s in series}) != len(series):
        raise EpsError(f"{name}: two series received the same label")

    # ---- were the plotted numbers given to only k decimals?  (panel level, all series pooled)
    rounding = decimal_rounding_test([v for s in series for v in s["_exact"]["value"]], cal["y"]["per_digit"])
    if rounding:
        k = rounding["decimals"]
        for s in series:   # strings, so that trailing zeros survive
            s["value_rounded"] = [fixed(Fraction(round(v * 10 ** k), 10 ** k), k) for v in s["_exact"]["value"]]

    # ---- per-axis calibration report
    def axis_report(axis: str) -> dict:
        c, title = cal[axis], scene["titles"].get(axis)
        data = [v for s in series for v in s["_exact"]["theta" if axis == "x" else "value"]]
        ulp = single_ulp(max(abs(v) for v in data))
        n = len(c["ps"])
        # limits are quoted to the last decimal place that is not finer than the resolution
        limit_decimals = max(decimals_for(c["per_digit"], 0) - 1, 0)
        return {
            "title": title["text"] if title else None,
            "title_decoded": bool(title and title["decoded"]),
            "title_font_size_ps": sig(title["font_size"]) if title and title["font_size"] else None,
            "ticks": [{"ps": float(p), "label": text} for p, text in zip(c["ps"], c["labels"])],
            "unlabelled_ticks_ps": [float(p) for p in c["unlabelled_ticks"]],
            "map": {"form": "data = intercept + slope * ps", "intercept": float(c["intercept"]),
                    "slope": float(c["slope"])},
            "tick_fit": {
                "n_ticks": n, "degrees_of_freedom": n - 2,
                "targets": "single(label)",
                "max_abs_residual_data": sig(c["max_residual"]),
                "max_abs_residual_ps": sig(c["max_residual"] / abs(c["slope"])),
                "max_abs_residual_ps_if_targets_were_exact_decimals":
                    sig(c["max_residual_decimal"] / abs(c["slope"])),
            },
            "limits_at_axes_box_edges": [float(fixed(v, limit_decimals)) for v in c["limits"]],
            "resolution": {
                "value_per_ps_digit": sig(c["per_digit"], 6),
                "single_precision_ulp": sig(ulp, 6),
                "abs_error_bound_vs_plotted_double": sig(c["per_digit"] / 2 + Fraction(ulp) / 2, 3),
            },
            "csv_decimals": theta_decimals if axis == "x" else value_decimals,
        }

    roles: dict = {}
    for o in eps["painted"]:
        roles[o.role] = roles.get(o.role, 0) + 1
    texts = [t for t in scene["titles"].values()] + [e["text"] for e in scene["entries"]]
    gaps = [g for t in texts for g in t["gaps_em"]]
    lines = scene["line_pos"]
    return {
        "figure": figure, "panel": panel, "file": name, "rows": rows,
        "report": {
            "figure": figure, "panel": panel,
            "eps": {
                "creator": eps["creator"], "creation_date": eps["creation_date"],
                "bounding_box": [float(v) for v in eps["bbox"]],
                "page_setup_matrix": [float(v) for v in eps["page_setup_matrix"]],
                "coordinate_decimals": decimals,
            },
            "axes_box_ps": {k: float(v) for k, v in box.items()},
            "axis_lines_ps": {f"{side}_{'y' if side in ('bottom', 'top') else 'x'}": float(lines[side])
                              for side in ("bottom", "top", "left", "right") if side in lines},
            "x_axis": axis_report("x"),
            "y_axis": axis_report("y"),
            "legend": {
                "box_ps": [float(v) for v in scene["legend_box"]] if scene["legend_box"] else None,
                "entries": legend,
            },
            "decimal_rounding": rounding,
            "series": series,
            "checks": {
                "painted_objects_by_role": dict(sorted(roles.items())),
                "painted_objects_total": len(eps["painted"]),
                "max_offset_tick_label_anchor_vs_tick_mark_ps": sig(scene["anchor_offset"]),
                "max_offset_legend_text_vs_sample_row_ps": sig(scene["row_offset"]),
                "glyph_strings_decoded": all(t["decoded"] for t in texts),
                "max_font_size_spread_within_string":
                    sig(max((t.get("size_spread", 0) for t in texts), default=0)),
                "max_letter_gap_em": sig(max((g for g in gaps if g <= SPACE_GAP_EM), default=0)),
                "min_word_gap_em": sig(min((g for g in gaps if g > SPACE_GAP_EM), default=0)),
            },
        },
    }


META = {
    "generator": "numerics/figures/extract_published_data.py",
    "source": "paper/*.eps (vector EPS written by MATLAB R2018a)",
    "coordinate_frame": "ps = page frame of the EPS body: PostScript points, x right, y DOWN from the top of "
                        "the bounding box (the file's page-setup matrix is [1 0 0 -1 0 H]). "
                        "Default user space is y_user = H - y",
    "calibration": "per axis, exact least-squares line through (tick-mark position, single(tick-label value)). "
                   "MATLAB places coordinates after rounding them to IEEE single precision, see tick_fit",
    "axes_box_ps": "the white axes-background rectangle. It carries the exact axis limits "
                   "(limits_at_axes_box_edges, quoted to the axis resolution), while the axis lines sit at "
                   "single(limit)",
    "resolution": {
        "value_per_ps_digit": "change of the data value when a ps coordinate changes by one unit of its last "
                              "stored decimal (coordinate_decimals). The rounding error is half of it",
        "single_precision_ulp": "spacing of single-precision numbers at the largest plotted magnitude. The "
                                "figure shows single(value), which is within half an ulp of the plotted double",
        "abs_error_bound_vs_plotted_double": "0.5 * value_per_ps_digit + 0.5 * single_precision_ulp",
    },
    "comparison_guidance": [
        "panel with decimal_rounding = null: |recomputed - value| <= abs_error_bound_vs_plotted_double of the "
        "y axis. Sharper: |single(recomputed) - value| <= about one value_per_ps_digit",
        "panel with decimal_rounding k: round(recomputed, k) must equal value_rounded. The unrounded "
        "recomputation may differ from value by up to 0.5*10^-k + abs_error_bound_vs_plotted_double",
    ],
    "decimal_rounding": "null, or the smallest k such that every plotted value equals single(a k-decimal "
                        "number) within 0.75 ps digit while the probability of that happening by accident, "
                        "at most ((ulp + 2*max deviation)/10^-k)^n for n distinct values, is below 1e-6.  If "
                        "present, the panel was drawn from numbers given to k decimals and "
                        "series[].value_rounded lists them, while series[].value and the CSV keep the direct "
                        "extraction",
    "text_decoding": "tick labels are character strings in the EPS, while axis titles and legend labels are glyph "
                     "outlines and are decoded with the outline codebook GLYPHS in the generator "
                     "(apostrophe = cmr10 quoteright, 'fi' = ligature)",
    "series_identification": "legend sample line and data polyline with identical colour, dash array and width",
    "csv": {"point": "1-based vertex index along the polyline as drawn (increasing theta)",
            "theta, value": "fixed decimals per file, see csv_decimals"},
}


def extract_all() -> list:
    return [extract_panel(*panel) for panel in PANELS]


def write_outputs(panels: list, out_dir: Path = OUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / CSV_NAME).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for p in panels:
            writer.writerows(p["rows"])
    reports = copy.deepcopy({p["file"]: p["report"] for p in panels})
    for report in reports.values():
        for s in report["series"]:
            del s["_exact"]
    document = {"_meta": META, "files": reports}
    text = to_json(document) + "\n"
    if json.loads(text) != document:
        raise EpsError("internal error: calibration JSON does not round-trip")
    (out_dir / JSON_NAME).write_bytes(text.encode("utf-8"))      # bytes: no newline translation on any platform


# --------------------------------------------------------------------------------------------------
# 6. Acceptance checks (--check).  They only read and never change the outputs.
# --------------------------------------------------------------------------------------------------

def check_theta_grid(panels: list) -> bool:
    """Every curve must have the expected number of vertices at the expected theta values."""
    ok = True
    print("\nTheta grid (expected: Figure 1 = 0.01, 0.1, ..., 0.9, 0.99 and Figure B.1 = 0, 0.1, ..., 1)")
    print("  ok = same number of points and max |theta - expected| <= x resolution (one ps digit)")
    print(f"  {'file':<12}{'series':<13}{'points':>6}  {'max |theta - expected|':>23}  {'x resolution':>12}")
    for p in panels:
        expected = [Fraction(t) for t in EXPECTED_THETA[p["figure"]]]
        resolution = p["report"]["x_axis"]["resolution"]["value_per_ps_digit"]
        for s in p["report"]["series"]:
            theta = s["_exact"]["theta"]
            same_length = len(theta) == len(expected)
            dev = float(max(abs(a - b) for a, b in zip(theta, expected))) if same_length else math.inf
            good = same_length and dev <= resolution
            ok &= good
            print(f"  {p['file']:<12}{s['label']:<13}{len(theta):>6}  {dev:>23.2e}  {resolution:>12.2e}"
                  f"  {'ok' if good else 'MISMATCH'}")
    return ok


def report_decimal_rounding(panels: list) -> None:
    print("\nDecimal rounding of the plotted numbers (information only, see decimal_rounding_test)")
    for p in panels:
        r = p["report"]["decimal_rounding"]
        text = "not rounded to <= %d decimals" % ROUNDING_MAX_DECIMALS
        if r:
            text = (f"all {r['n_distinct_values']} distinct values are {r['decimals']}-decimal numbers "
                    f"(max deviation {r['max_abs_deviation_in_ps_digits']} ps digit, "
                    f"chance <= {r['chance_probability']:.1e})")
        print(f"  {p['file']:<12}Figure {p['figure']}({p['panel']}): {text}")


def check_against_reference(panels: list) -> bool:
    """Figure B.1 only: extracted values against the MATLAB-computed reference table."""
    ok = True
    print(f"\nFigure B.1 against {REFERENCE_B1_CSV.relative_to(REPO_ROOT)}")
    print("  digit = value_per_ps_digit, ulp = single-precision spacing at the data, range = y-axis range")
    print("  bound = 0.5 digit + 0.5 ulp (rounding of the stored coordinate + single-precision placement)")
    print("  ok    = max|ext-single(ref)| <= 1 digit  and  max|ext-ref| <= bound + 0.5 digit")
    with REFERENCE_B1_CSV.open(newline="", encoding="utf-8") as handle:
        reference = list(csv.DictReader(handle))
    print(f"  {'panel':<6}{'series':<13}{'digit':>10}{'ulp':>10}{'max|ext-ref|':>14}{'/range':>10}"
          f"{'/digit':>8}{'/bound':>8}{'max|ext-single(ref)|':>22}{'/digit':>8}")
    for p in panels:
        if p["figure"] != "B.1":
            continue
        y = p["report"]["y_axis"]
        digit = y["resolution"]["value_per_ps_digit"]
        y_range = abs(y["limits_at_axes_box_edges"][1] - y["limits_at_axes_box_edges"][0])
        worst = 0.0
        for s in p["report"]["series"]:
            row_head = f"  {p['panel']:<6}{s['label']:<13}"
            column = f"{p['panel']}_{s['label'].removeprefix('Scenario ')}"   # reference column, e.g. a_GS, b_0
            if column not in reference[0] or len(reference) != s["n_points"]:
                print(row_head + " no matching reference column / row count  MISMATCH")
                ok = False
                continue
            ref = [Fraction(row[column]) for row in reference]
            ref_theta = [Fraction(row["theta"]) for row in reference]
            if max(abs(a - b) for a, b in zip(s["_exact"]["theta"], ref_theta)) > Fraction(1, 10 ** 6):
                print(row_head + " theta grid differs from the reference  MISMATCH")
                ok = False
                continue
            value = s["_exact"]["value"]
            dev = float(max(abs(v - r) for v, r in zip(value, ref)))
            dev_single = float(max(abs(v - single(r)) for v, r in zip(value, ref)))
            ulp = single_ulp(max(abs(r) for r in ref))
            bound = 0.5 * digit + 0.5 * ulp
            good = dev_single <= digit and dev <= bound + 0.5 * digit
            ok &= good
            worst = max(worst, dev)
            print(row_head + f"{digit:>10.2e}{ulp:>10.2e}{dev:>14.3e}{dev / y_range:>10.1e}{dev / digit:>8.2f}"
                  f"{dev / bound:>8.2f}{dev_single:>22.3e}{dev_single / digit:>8.2f}"
                  f"  {'ok' if good else 'MISMATCH'}")
        print(f"  panel {p['panel']} ({p['file']}): max |extracted - reference| = {worst:.3e} "
              f"= {worst / y_range:.1e} of the y-axis range {y_range:g}")
    return ok


def run_checks(panels: list) -> bool:
    ok = check_theta_grid(panels)
    report_decimal_rounding(panels)
    ok = check_against_reference(panels) and ok
    print("\nacceptance:", "PASS" if ok else "FAIL")
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="also print the acceptance checks")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR, help="where to write the two outputs")
    args = parser.parse_args(argv)

    panels = extract_all()
    write_outputs(panels, args.out_dir)
    for p in panels:
        r = p["report"]
        curves = " | ".join(f"{s['label']} [{s['color']}, {s['dash']}]: {s['n_points']} points"
                           for s in r["series"])
        print(f"{p['file']:<12} Figure {p['figure']}({p['panel']})  {curves}")
    print(f"wrote {CSV_NAME} ({sum(len(p['rows']) for p in panels)} rows) and {JSON_NAME} to {args.out_dir}")
    if args.check:
        return 0 if run_checks(panels) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
