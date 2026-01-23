import csv
import re
from pathlib import Path
from typing import Optional
from collections import Counter

from .normalizer import normalize_phone_number


class ColumnDetector:
    SAMPLE_SIZE = 100

    SURNAME_PATTERNS = [
        "성",
        "Last Name",
        "last_name",
        "lastname",
        "surname",
    ]
    
    FIRST_NAME_PATTERNS = [
        "이름",
        "First Name",
        "first_name",
        "firstname",
        "given name",
    ]
    
    MIDDLE_NAME_PATTERNS = [
        "Middle Name",
        "middle_name",
        "middlename",
    ]
    
    FULL_NAME_PATTERNS = [
        "이름 (휴대폰에 저장될 이름)",
        "Name",
        "name",
        "성명",
        "성함",
        "Full Name",
        "full_name",
    ]

    PHONE_PATTERNS = [
        "Mobile Phone",
        "mobile_phone",
        "mobilephone",
        "Phone",
        "phone",
        "telephone",
        "휴대폰번호",
        "휴대폰",
        "전화번호",
        "연락처",
    ]

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = Path(file_path)
        self.encoding = encoding
        self._headers: list[str] = []
        self._sample_rows: list[dict] = []
        self._load_sample()

    def _load_sample(self) -> None:
        suffix = self.file_path.suffix.lower()

        if suffix in [".xlsx", ".xls"]:
            self._load_excel_sample()
        else:
            self._load_csv_sample()

    def _load_excel_sample(self) -> None:
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl 패키지가 필요합니다: pip install openpyxl")

        wb = openpyxl.load_workbook(self.file_path, read_only=True, data_only=True)
        ws = wb.active

        rows_iter = ws.iter_rows(values_only=True)
        first_row = next(rows_iter, None)
        
        if first_row and len(first_row) > 0 and first_row[0]:
            first_cell_text = str(first_row[0]).strip()
            if first_cell_text.startswith('*'):
                header_row = next(rows_iter, None)
            else:
                header_row = first_row
        else:
            header_row = first_row

        if header_row:
            self._headers = [
                str(h) if h else f"Column{i}" for i, h in enumerate(header_row)
            ]

        self._sample_rows = []
        for i, row in enumerate(rows_iter):
            if i >= self.SAMPLE_SIZE:
                break
            row_dict = {}
            for j, value in enumerate(row):
                if j < len(self._headers):
                    row_dict[self._headers[j]] = str(value) if value else ""
            self._sample_rows.append(row_dict)

        wb.close()

    def _load_csv_sample(self) -> None:
        encodings_to_try = [self.encoding, "utf-8-sig", "cp949", "euc-kr"]

        for enc in encodings_to_try:
            try:
                with open(self.file_path, "r", encoding=enc, newline="") as f:
                    reader = csv.DictReader(f)
                    self._headers = [self._clean_header(h) for h in reader.fieldnames] if reader.fieldnames else []
                    self._sample_rows = []
                    for i, row in enumerate(reader):
                        if i >= self.SAMPLE_SIZE:
                            break
                        self._sample_rows.append(row)
                self.encoding = enc
                return
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise ValueError(
            f"Cannot read CSV file with supported encodings: {self.file_path}"
        )
    
    def _clean_header(self, header: str) -> str:
        if not header:
            return header
        cleaned = header.strip()
        cleaned = cleaned.lstrip('\ufeff')
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        if cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1]
        return cleaned.strip()

    def get_headers(self) -> list[str]:
        return self._headers.copy()

    def detect_name_columns(self) -> dict[str, Optional[str]]:
        result: dict[str, Optional[str]] = {
            "surname": None,
            "first_name": None,
            "middle_name": None,
            "full_name": None
        }
        
        for pattern in self.SURNAME_PATTERNS:
            for header in self._headers:
                if pattern.lower() == header.lower().strip():
                    result["surname"] = header
                    break
            if result["surname"]:
                break
        
        for pattern in self.FIRST_NAME_PATTERNS:
            for header in self._headers:
                if pattern.lower() == header.lower().strip():
                    result["first_name"] = header
                    break
            if result["first_name"]:
                break
        
        for pattern in self.MIDDLE_NAME_PATTERNS:
            for header in self._headers:
                if pattern.lower() == header.lower().strip():
                    result["middle_name"] = header
                    break
            if result["middle_name"]:
                break
        
        for pattern in self.FULL_NAME_PATTERNS:
            for header in self._headers:
                if pattern.lower() == header.lower().strip():
                    result["full_name"] = header
                    break
            if result["full_name"]:
                break
        
        return result
    
    def detect_name_column(self) -> Optional[str]:
        return self._headers[0] if self._headers else None

    def detect_phone_column(self) -> Optional[str]:
        for pattern in self.PHONE_PATTERNS:
            for header in self._headers:
                if pattern.lower() == header.lower().strip():
                    return header

        phone_counts: Counter[str] = Counter()

        for header in self._headers:
            count = 0
            for row in self._sample_rows:
                value = row.get(header, "").strip()
                if value:
                    result = normalize_phone_number(value)
                    if result.status == "valid":
                        count += 1
            if count > 0:
                phone_counts[header] = count

        if phone_counts:
            return phone_counts.most_common(1)[0][0]

        for header in self._headers:
            for row in self._sample_rows:
                value = row.get(header, "").strip()
                if value and re.search(r"010[-\s]?\d{4}[-\s]?\d{4}", value):
                    return header

        return None

    def get_column_stats(self) -> dict:
        stats = {}
        for header in self._headers:
            valid_count = 0
            total_count = 0
            for row in self._sample_rows:
                value = row.get(header, "").strip()
                if value and re.search(r"\d", value):
                    total_count += 1
                    result = normalize_phone_number(value)
                    if result.status == "valid":
                        valid_count += 1
            if total_count > 0:
                stats[header] = {
                    "valid_010": valid_count,
                    "has_digits": total_count,
                    "sample_size": len(self._sample_rows),
                }
        return stats
