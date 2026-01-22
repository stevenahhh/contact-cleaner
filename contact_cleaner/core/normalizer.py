import re
from typing import NamedTuple, Optional


class NormalizeResult(NamedTuple):
    normalized: Optional[str]
    status: str
    original: str


_STRIP_PATTERN = re.compile(r"[\s\-\(\)]")
_NON_DIGIT_PATTERN = re.compile(r"[^\d]")

_LANDLINE_PREFIXES = ("02", "031", "032", "033", "041", "042", "043", "044",
                      "051", "052", "053", "054", "055", "061", "062", "063", "064")
_SERVICE_PREFIXES = ("1588", "1577", "1544", "1566", "1600", "1644", "1661", "1670", "1688", "1899", "080")
_OLD_MOBILE_PREFIXES = ("011", "016", "017", "018", "019")


def normalize_phone_number(phone: str) -> NormalizeResult:
    if not phone:
        return NormalizeResult(normalized=None, status="empty", original="")

    original = str(phone).strip()
    cleaned = _STRIP_PATTERN.sub("", original)

    if cleaned.startswith("+82"):
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("82") and len(cleaned) >= 10:
        cleaned = "0" + cleaned[2:]

    cleaned = _NON_DIGIT_PATTERN.sub("", cleaned)

    if cleaned.startswith("10") and len(cleaned) == 10:
        cleaned = "0" + cleaned

    if not cleaned:
        return NormalizeResult(normalized=None, status="empty", original=original)

    if cleaned.startswith(_LANDLINE_PREFIXES):
        return NormalizeResult(normalized=None, status="landline", original=original)

    if cleaned.startswith("070"):
        return NormalizeResult(normalized=None, status="internet", original=original)

    if cleaned.startswith(_SERVICE_PREFIXES):
        return NormalizeResult(normalized=None, status="service", original=original)

    if cleaned.startswith(_OLD_MOBILE_PREFIXES):
        return NormalizeResult(normalized=None, status="old_mobile", original=original)

    if not cleaned.startswith("010"):
        return NormalizeResult(normalized=None, status="invalid", original=original)

    if len(cleaned) != 11:
        return NormalizeResult(normalized=None, status="invalid", original=original)

    formatted = f"{cleaned[0:3]}-{cleaned[3:7]}-{cleaned[7:11]}"

    return NormalizeResult(normalized=formatted, status="valid", original=original)
