"""Shared normalization helper (extracted from 00_build_master for reuse)."""
from __future__ import annotations
import re


def norm_key(s) -> str:
    """Aggressive canonical key: upper, strip, collapse spaces/punct."""
    if s is None:
        return ""
    try:
        if isinstance(s, float) and s != s:      # NaN
            return ""
    except TypeError:
        pass
    s = str(s).upper().strip()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()
