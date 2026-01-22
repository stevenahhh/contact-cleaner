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

        name_columns = self.detector.detect_name_columns()
        phone_col = self.detector.detect_phone_column()
        encoding = self.detector.encoding

        original_data = []
        transformed_data = []
        comparison_data = []
        stats = {"O": 0, "X": 0, "△": 0}

        rows = self._read_rows(encoding)

        for row in rows:
            name = self._extract_name_from_row(row, name_columns)

            all_phones = self._find_all_valid_phones_in_row(row)
            
            if not all_phones:
                original_data.append(
                    {
                        "이름": name,
                        "원본 전화번호": "",
                    }
                )
                comparison_data.append(
                    {
                        "이름": name,
                        "원본 전화번호": "",
                        "변환됨": "",
                        "검증": "",
                    }
                )
            else:
                for phone in all_phones:
                    original_data.append(
                        {
                            "이름": name,
                            "원본 전화번호": phone,
                        }
                    )

                    if phone:
                        transformed_data.append(
                            {
                                "이름": name,
                                "변환됨": phone,
                            }
                        )

                    comparison_data.append(
                        {
                            "이름": name,
                            "원본 전화번호": phone,
                            "변환됨": phone,
                            "검증": "",
                        }
                    )

        return ProcessResult(
            original_data=original_data,
            transformed_data=transformed_data,
            comparison_data=comparison_data,
            stats=stats,
            detected_phone_col=phone_col,
            detected_name_col=self._get_name_col_summary(name_columns),
            encoding=encoding,
        )
    
    def _extract_name_from_row(self, row: dict, name_columns: dict[str, Optional[str]]) -> str:
        surname = self._clean_value(row.get(name_columns["surname"], "")) if name_columns["surname"] else ""
        first_name = self._clean_value(row.get(name_columns["first_name"], "")) if name_columns["first_name"] else ""
        middle_name = self._clean_value(row.get(name_columns["middle_name"], "")) if name_columns["middle_name"] else ""
        full_name = self._clean_value(row.get(name_columns["full_name"], "")) if name_columns["full_name"] else ""
        
        if surname and first_name:
            if first_name == "'" or first_name == '"':
                return surname
            parts = [surname, first_name]
            if middle_name and middle_name not in ("'", '"'):
                parts.append(middle_name)
            return " ".join(parts)
        elif surname:
            return surname
        elif first_name:
            if first_name in ("'", '"'):
                return ""
            parts = [first_name]
            if middle_name and middle_name not in ("'", '"'):
                parts.append(middle_name)
            return " ".join(parts)
        elif full_name:
            return full_name
        else:
            has_any_name_column = any([
                name_columns["surname"],
                name_columns["first_name"],
                name_columns["middle_name"],
                name_columns["full_name"]
            ])
            
            if has_any_name_column:
                return ""
            
            for header, value in row.items():
                from .normalizer import normalize_phone_number
                cleaned = self._clean_value(value)
                if cleaned and cleaned not in ("'", '"'):
                    result = normalize_phone_number(cleaned)
                    if result.status != "valid":
                        return cleaned
            return ""
    
    def _clean_value(self, value: str) -> str:
        if not value:
            return ""
        cleaned = str(value).strip()
        if cleaned == "'":
            return ""
        if cleaned.startswith("'") and len(cleaned) > 1:
            cleaned = cleaned[1:]
        return cleaned.strip()
    
    def _get_name_col_summary(self, name_columns: dict[str, Optional[str]]) -> Optional[str]:
        cols = []
        if name_columns["surname"]:
            cols.append(name_columns["surname"])
        if name_columns["first_name"]:
            cols.append(name_columns["first_name"])
        if name_columns["middle_name"]:
            cols.append(name_columns["middle_name"])
        if name_columns["full_name"]:
            cols.append(name_columns["full_name"])
        
        return "+".join(cols) if cols else None

    def _find_all_valid_phones_in_row(self, row: dict) -> list[str]:
        phones = []
        seen = set()
        for header, value in row.items():
            value = str(value).strip()
            if value:
                result = normalize_phone_number(value)
                if result.status == "valid" and result.normalized not in seen:
                    phones.append(result.normalized)
                    seen.add(result.normalized)
        return phones

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
        first_row = next(rows_iter, None)
        
        if not first_row:
            wb.close()
            return []
        
        if all(cell is None or str(cell).strip() == '' for cell in first_row):
            header_row = next(rows_iter, None)
        else:
            header_row = first_row

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
            if reader.fieldnames:
                cleaned_fieldnames = [self._clean_header(h) for h in reader.fieldnames]
            else:
                cleaned_fieldnames = []
            
            for row in reader:
                cleaned_row = {}
                for original_header, cleaned_header in zip(reader.fieldnames or [], cleaned_fieldnames):
                    cleaned_row[cleaned_header] = row.get(original_header, "")
                rows.append(cleaned_row)
        return rows
    
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
