"""
text_cleaner.py

Pure text normalization utilities.
All functions are stateless and side-effect-free.
No business logic — input → cleaned output only.
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# Individual cleaning steps
# ---------------------------------------------------------------------------

def remove_control_characters(text: str) -> str:
    """
    Strip null bytes, non-printable control characters, and soft hyphens.
    Preserves standard whitespace: space (0x20), tab (0x09), newline (0x0A),
    carriage return (0x0D).
    """
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\xad]", "", text)


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode to NFC (canonical composition).
    Replaces common ligatures and typographic substitutions with ASCII equivalents
    so downstream regex matching works reliably across PDF encodings.

    Examples:
        ﬁ → fi    ﬂ → fl    — → -    " " → " "    … → ...
    """
    # NFC normalization first
    text = unicodedata.normalize("NFC", text)

    # Ligature expansion (common in PDF fonts)
    ligatures = {
        "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
        "\ufb03": "ffi", "\ufb04": "ffl",
        "\u2013": "-",   # en-dash
        "\u2014": "-",   # em-dash
        "\u2018": "'", "\u2019": "'",   # smart single quotes
        "\u201c": '"', "\u201d": '"',   # smart double quotes
        "\u2026": "...",                 # ellipsis
        "\u00b7": "-",                   # middle dot (used as bullet in some PDFs)
        "\u2022": "-",                   # bullet
        "\u25cf": "-",                   # black circle bullet
    }
    for src, dst in ligatures.items():
        text = text.replace(src, dst)

    return text


def normalize_whitespace(text: str) -> str:
    """
    Within each line: collapse runs of spaces/tabs to a single space and strip edges.
    Preserves newlines — they carry structural meaning for section detection.
    """
    lines = text.splitlines()
    return "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in lines)


def collapse_blank_lines(text: str, max_consecutive: int = 2) -> str:
    """
    Reduce runs of blank lines to at most `max_consecutive`.
    Prevents runaway whitespace from low-quality PDF extractions.
    """
    pattern = r"(\n[ \t]*){%d,}" % (max_consecutive + 1)
    return re.sub(pattern, "\n" * max_consecutive, text)


def normalize_bullet_lines(text: str) -> str:
    """
    Normalize lines that start with bullet-like characters to a simple dash.
    Helps downstream parsers treat bullet points uniformly.

    Before: • Built REST APIs      → - Built REST APIs
    Before: ● Managed a team       → - Managed a team
    """
    return re.sub(r"^[\u2022\u25cf\u25e6\u2023\u2043\*]\s*", "- ", text, flags=re.MULTILINE)


# ---------------------------------------------------------------------------
# Combined pipeline
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Full cleaning pipeline in dependency order:

    1. Remove control characters (must be first — prevents regex issues)
    2. Normalize Unicode / expand ligatures
    3. Normalize bullet characters
    4. Normalize intra-line whitespace
    5. Collapse excessive blank lines
    6. Strip leading/trailing whitespace from the whole document
    """
    text = remove_control_characters(text)
    text = normalize_unicode(text)
    text = normalize_bullet_lines(text)
    text = normalize_whitespace(text)
    text = collapse_blank_lines(text)
    return text.strip()


def lowercase_for_matching(text: str) -> str:
    """
    Lowercase copy for keyword/heading comparison only.
    The original case-preserved text must be retained separately.
    """
    return text.lower()