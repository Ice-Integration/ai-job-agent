from __future__ import annotations

import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all|previous|earlier) instructions",
    r"reveal (the )?(system|developer) prompt",
    r"exfiltrate",
    r"send .*secret",
    r"api[_ -]?key",
]


def inspect_text(text: str) -> tuple[bool, list[str]]:
    findings = [pattern for pattern in SUSPICIOUS_PATTERNS if re.search(pattern, text, flags=re.I)]
    return not findings, findings
