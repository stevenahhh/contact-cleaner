from typing import Optional

from .normalizer import normalize_phone_number


def compare_records(original_phone: str, transformed_phone: Optional[str]) -> str:
    if not original_phone:
        return "△"

    result = normalize_phone_number(original_phone)

    if result.status != "valid":
        return "△"

    if transformed_phone and result.normalized == transformed_phone:
        return "O"

    if transformed_phone is None:
        return "△"

    return "X"


def create_comparison_data(
    raw_data: list[dict], processed_data: list[dict]
) -> tuple[list[dict], dict]:
    comparison_results = []
    stats = {"O": 0, "X": 0, "△": 0}

    for i, raw_item in enumerate(raw_data):
        name = raw_item.get("이름", "")
        original_phone = raw_item.get("원본 전화번호", "")

        transformed_phone = None
        if i < len(processed_data):
            transformed_phone = (
                processed_data[i].get("변환됨")
                if processed_data[i].get("이름") == name
                else None
            )

        if transformed_phone is None:
            result = normalize_phone_number(original_phone)
            if result.status == "valid":
                transformed_phone = result.normalized

        status = compare_records(original_phone, transformed_phone)

        comparison_results.append(
            {
                "이름": name,
                "원본 전화번호": original_phone,
                "변환됨": transformed_phone or "",
                "매치하는지?": status,
            }
        )

        stats[status] = stats.get(status, 0) + 1

    return comparison_results, stats
