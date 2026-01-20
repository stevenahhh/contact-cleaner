import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from contact_cleaner.core.processor import ContactProcessor


def check_duplicates(file1_path: str, file2_path: str):
    print(f"\n파일1: {Path(file1_path).name}")
    print(f"파일2: {Path(file2_path).name}")
    print("=" * 60)

    processor1 = ContactProcessor(file1_path)
    result1 = processor1.process()

    processor2 = ContactProcessor(file2_path)
    result2 = processor2.process()

    data1 = [
        {"이름": row["이름"], "변환됨": row["변환됨"]}
        for row in result1.comparison_data
        if row["변환됨"]
    ]

    data2 = [
        {"이름": row["이름"], "변환됨": row["변환됨"]}
        for row in result2.comparison_data
        if row["변환됨"]
    ]

    print(f"\n파일1 유효 번호: {len(data1)}개")
    print(f"파일2 유효 번호: {len(data2)}개")

    all_data = data1 + data2

    unique_map = {}
    for item in all_data:
        name = item["이름"].strip()
        phone = item["변환됨"]
        key = (name, phone)

        if key not in unique_map:
            unique_map[key] = item

    unique_list = list(unique_map.values())

    phone_to_names = {}
    for item in unique_list:
        name = item["이름"]
        phone = item["변환됨"]

        if phone not in phone_to_names:
            phone_to_names[phone] = []
        phone_to_names[phone].append(name)

    deduplicated = {}

    for item in unique_list:
        name = item["이름"]
        phone = item["변환됨"]

        name_clean = name.replace(" ", "")

        other_names = phone_to_names.get(phone, [])

        if len(other_names) > 1:
            similar_found = False
            for other_name in other_names:
                if other_name != name:
                    other_clean = other_name.replace(" ", "")
                    if name_clean in other_clean or other_clean in name_clean:
                        similar_found = True
                        canonical_key = (min(name, other_name), phone)
                        if canonical_key not in deduplicated:
                            deduplicated[canonical_key] = ("O", name, phone)
                        break

            if not similar_found:
                key = (name, phone)
                if key not in deduplicated:
                    deduplicated[key] = ("번호", name, phone)
        else:
            key = (name, phone)
            if key not in deduplicated:
                deduplicated[key] = ("X", name, phone)

    stats = {"O": [], "이름": [], "번호": [], "X": []}

    for status, name, phone in deduplicated.values():
        stats[status].append((name, phone))

    print("\n" + "=" * 60)
    print("중복 검사 결과:")
    print("=" * 60)

    total_duplicates = len(stats["O"]) + len(stats["이름"]) + len(stats["번호"])

    print(f"\n총 병합 후 유니크 항목: {len(deduplicated)}개")
    print(f"중복 항목: {total_duplicates}개")
    print(f"중복 없는 항목: {len(stats['X'])}개")

    print(f"\n[O] 이름+번호 모두 중복: {len(stats['O'])}개")
    if stats["O"]:
        for name, phone in stats["O"][:10]:
            print(f"  - {name} / {phone}")
        if len(stats["O"]) > 10:
            print(f"  ... 외 {len(stats['O']) - 10}개")

    print(f"\n[이름] 이름만 중복: {len(stats['이름'])}개")
    if stats["이름"]:
        for name, phone in stats["이름"][:10]:
            print(f"  - {name} / {phone}")
        if len(stats["이름"]) > 10:
            print(f"  ... 외 {len(stats['이름']) - 10}개")

    print(f"\n[번호] 번호만 중복: {len(stats['번호'])}개")
    if stats["번호"]:
        for name, phone in stats["번호"][:10]:
            print(f"  - {name} / {phone}")
        if len(stats["번호"]) > 10:
            print(f"  ... 외 {len(stats['번호']) - 10}개")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python check_duplicates.py <파일1> <파일2>")
        print("예시: python check_duplicates.py file1.csv file2.csv")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    if not Path(file1).exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {file1}")
        sys.exit(1)

    if not Path(file2).exists():
        print(f"오류: 파일을 찾을 수 없습니다 - {file2}")
        sys.exit(1)

    check_duplicates(file1, file2)
