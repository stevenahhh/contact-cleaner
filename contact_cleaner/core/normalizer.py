import re
from typing import NamedTuple, Optional


class NormalizeResult(NamedTuple):
    normalized: Optional[str]
    status: str
    original: str


def normalize_phone_number(phone: str) -> NormalizeResult:
    if not phone:
        return NormalizeResult(normalized=None, status="empty", original="")

    original = str(phone).strip()
    cleaned = re.sub(r"[\s\-\(\)]", "", original)

    if cleaned.startswith("+82"):
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("82") and len(cleaned) >= 10:
        cleaned = "0" + cleaned[2:]

    cleaned = re.sub(r"[^\d]", "", cleaned)

    if cleaned.startswith("10") and len(cleaned) == 10:
        cleaned = "0" + cleaned

    if not cleaned:
        return NormalizeResult(normalized=None, status="empty", original=original)

    if (
        cleaned.startswith("02")
        or cleaned.startswith("031")
        or cleaned.startswith("032")
        or cleaned.startswith("033")
        or cleaned.startswith("041")
        or cleaned.startswith("042")
        or cleaned.startswith("043")
        or cleaned.startswith("044")
        or cleaned.startswith("051")
        or cleaned.startswith("052")
        or cleaned.startswith("053")
        or cleaned.startswith("054")
        or cleaned.startswith("055")
        or cleaned.startswith("061")
        or cleaned.startswith("062")
        or cleaned.startswith("063")
        or cleaned.startswith("064")
    ):
        return NormalizeResult(normalized=None, status="landline", original=original)

    if cleaned.startswith("070"):
        return NormalizeResult(normalized=None, status="internet", original=original)

    if (
        cleaned.startswith("1588")
        or cleaned.startswith("1577")
        or cleaned.startswith("1544")
        or cleaned.startswith("1566")
        or cleaned.startswith("1600")
        or cleaned.startswith("1644")
        or cleaned.startswith("1661")
        or cleaned.startswith("1670")
        or cleaned.startswith("1688")
        or cleaned.startswith("1899")
        or cleaned.startswith("080")
    ):
        return NormalizeResult(normalized=None, status="service", original=original)

    if (
        cleaned.startswith("011")
        or cleaned.startswith("016")
        or cleaned.startswith("017")
        or cleaned.startswith("018")
        or cleaned.startswith("019")
    ):
        return NormalizeResult(normalized=None, status="old_mobile", original=original)

    if not cleaned.startswith("010"):
        return NormalizeResult(normalized=None, status="invalid", original=original)

    if len(cleaned) != 11:
        return NormalizeResult(normalized=None, status="invalid", original=original)

    formatted = f"{cleaned[0:3]}-{cleaned[3:7]}-{cleaned[7:11]}"

    if not re.match(r"^010-\d{4}-\d{4}$", formatted):
        return NormalizeResult(normalized=None, status="invalid", original=original)

    return NormalizeResult(normalized=formatted, status="valid", original=original)
