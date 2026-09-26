"""
01_extract-stage support: shared dirty-data writers for raw source files.

Every "raw" file is deliberately imperfect: mixed date formats, mixed decimal
separators, whitespace, case noise, blank rows, nulls, duplicates, invalid codes.
Raw files are WRITE-ONCE evidence and never edited afterwards.
"""
from __future__ import annotations
import params as P
from datetime import date, datetime
import numpy as np


# ------------------------------------------------------------------ dates
def fmt_date(d: date, rng: np.random.Generator) -> str:
    """Emit a date string in one of several formats, chosen at random."""
    f = P.DATE_FORMATS[rng.integers(0, len(P.DATE_FORMATS))]
    return d.strftime(f)


# ------------------------------------------------------------------ decimals
def fmt_num(v: float, rng: np.random.Generator, dp: int = 2) -> str:
    """Emit a number as text in one of three locale styles (ID / EN / plain)."""
    s = f"{abs(v):,.{dp}f}"
    style = P.DECIMAL_STYLES[rng.integers(0, len(P.DECIMAL_STYLES))]
    if style == "id":
        return ("-" if v < 0 else "") + s.replace(",", "|").replace(".", ",").replace("|", ".")
    if style == "en":
        return ("-" if v < 0 else "") + s
    return ("-" if v < 0 else "") + s.replace(",", "")


# ------------------------------------------------------------------ string noise
def messy(s: str, rng: np.random.Generator) -> str:
    """Leading/trailing whitespace + random case violence."""
    s = f" {s} " if rng.random() < 0.30 else s
    r = rng.random()
    if r < 0.25:
        s = s.upper()
    elif r < 0.50:
        s = s.lower()
    elif r < 0.65:
        s = s.title()
    return s


def maybe_null(rng: np.random.Generator, p: float = P.P_NULL) -> bool:
    return bool(rng.random() < p)


def blank_row(rng: np.random.Generator, p: float = 0.004) -> bool:
    return bool(rng.random() < p)

# ------------------------------------------------------------------ source-system aware helpers
def fmt_date_for(d: date, rng: np.random.Generator, system: str = None) -> str:
    """Emit date in the format preferred by a source system, with occasional noise."""
    if system and system in P.SOURCE_SYSTEMS:
        fmt = P.SOURCE_SYSTEMS[system]["date_fmt"]
        # occasional cross-system noise
        if rng.random() < 0.05:
            fmt = rng.choice(P.DATE_FORMATS)
        return d.strftime(fmt)
    return fmt_date(d, rng)


def fmt_num_for(v: float, rng: np.random.Generator, system: str = None, dp: int = 2) -> str:
    """Emit number in the decimal style preferred by a source system, with occasional noise."""
    style = None
    if system and system in P.SOURCE_SYSTEMS:
        style = P.SOURCE_SYSTEMS[system]["dec_style"]
        if rng.random() < 0.05:
            style = rng.choice(P.DECIMAL_STYLES)
    s = f"{abs(v):,.{dp}f}"
    if style == "id":
        return ("-" if v < 0 else "") + s.replace(",", "|").replace(".", ",").replace("|", ".")
    if style == "en":
        return ("-" if v < 0 else "") + s
    return ("-" if v < 0 else "") + s.replace(",", "")
