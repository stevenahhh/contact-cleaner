import csv
from pathlib import Path
from typing import NamedTuple, Optional

from .normalizer import normalize_phone_number
from .detector import ColumnDetector


class ProcessResult(NamedTuple):
    original_data: list[dict]
    transformed_data: list[dict]
    comparison_data: list[dict]
    stats: dict
    detected_phone_col: Optional[str]
    detected_name_col: Optional[str]
    encoding: str


class ContactProcessor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.detector: Optional[ColumnDetector] = None

    def process(self) -> ProcessResult:
        self.detector = ColumnDetector(str(self.file_path))

        name_col = self.detector.detect_name_column()
        phone_col = self.detector.detect_phone_column()
        encoding = self.detector.encoding

        original_data = []
        transformed_data = []
        comparison_data = []
        stats = {"O": 0, "X": 0, "△": 0}

        rows = self._read_rows(encoding)

        for row in rows:
            name = row.get(name_col, "").strip() if name_col else ""

            original_phone = ""
            normalized_phone = None

            if phone_col and row.get(phone_col, "").strip():
                original_phone = row.get(phone_col, "").strip()
                result = normalize_phone_number(original_phone)
                if result.status == "valid":
                    normalized_phone = result.normalized

            if not normalized_phone:
                normalized_phone = self._find_valid_phone_in_other_columns(
                    row, phone_col
                )
                if normalized_phone and not original_phone:
                    original_phone = normalized_phone

            original_data.append(
                {
                    "이름": name,
                    "원본 전화번호": original_phone,
                }
            )

            if name and normalized_phone:
                transformed_data.append(
                    {
                        "이름": name,
                        "변환됨": normalized_phone,
                    }
                )

            status = self._determine_status(original_phone, normalized_phone)
            comparison_data.append(
                {
                    "이름": name,
                    "원본 전화번호": original_phone,
                    "변환됨": normalized_phone or "",
                    "검증": status,
                }
            )
            stats[status] += 1

        return ProcessResult(
            original_data=original_data,
            transformed_data=transformed_data,
            comparison_data=comparison_data,
            stats=stats,
            detected_phone_col=phone_col,
            detected_name_col=name_col,
            encoding=encoding,
        )

    def _find_valid_phone_in_other_columns(
        self, row: dict, skip_col: Optional[str]
    ) -> Optional[str]:
        for header, value in row.items():
            if header == skip_col:
                continue
            value = str(value).strip()
            if value:
                result = normalize_phone_number(value)
                if result.status == "valid":
                    return result.normalized
        return None

    def _read_rows(self, encoding: str) -> list[dict]:
        suffix = self.file_path.suffix.lower()

        if suffix in [".xlsx", ".xls"]:
            return self._read_excel_rows()
        else:
            return self._read_csv_rows(encoding)

    def _read_excel_rows(self) -> list[dict]:
        import openpyxl

        wb = openpyxl.load_workbook(self.file_path, read_only=True, data_only=True)
        ws = wb.active

        rows_iter = ws.iter_rows(values_only=True)
        header_row = next(rows_iter, None)

        if not header_row:
            wb.close()
            return []

        headers = [str(h) if h else f"Column{i}" for i, h in enumerate(header_row)]

        rows = []
        for row in rows_iter:
            row_dict = {}
            for j, value in enumerate(row):
                if j < len(headers):
                    row_dict[headers[j]] = str(value) if value else ""
            rows.append(row_dict)

        wb.close()
        return rows

    def _read_csv_rows(self, encoding: str) -> list[dict]:
        rows = []
        with open(self.file_path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows

    def _determine_status(
        self, original_phone: str, normalized_phone: Optional[str]
    ) -> str:
        if not original_phone:
            return "△"

        result = normalize_phone_number(original_phone)

        if result.status != "valid":
            return "△"

        if normalized_phone and result.normalized == normalized_phone:
            return "O"

        return "X"
