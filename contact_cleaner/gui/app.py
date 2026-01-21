import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from contact_cleaner.gui.theme import init_theme
from contact_cleaner.gui.widgets import (
    FileListFrame,
    StatusLegend,
    ProgressFrame,
    LogFrame,
)
from contact_cleaner.core.processor import ContactProcessor
from contact_cleaner.utils.file_utils import (
    create_output_structure,
    copy_original_file,
    save_transformed_csv,
    save_styled_excel,
    open_folder_in_explorer,
    get_work_folder,
)


class ContactCleanerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("주소록 정리 v1.2.0")
        self.geometry("900x800")
        self.minsize(800, 600)

        init_theme(self)
        self._setup_ui()

    def _setup_ui(self):
        from tkinter import font as tkfont

        self.header_font = tkfont.Font(family="Malgun Gothic", size=20, weight="bold")
        self.default_font_bold = tkfont.Font(
            family="Malgun Gothic", size=10, weight="bold"
        )
        self.small_font = tkfont.Font(family="Malgun Gothic", size=9)
        self.version_font = tkfont.Font(family="Malgun Gothic", size=8)

        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        lists_container = ttk.Frame(main_container)
        lists_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.source_list = FileListFrame(
            lists_container, title="1. 정리할 원본 파일", on_add=self.add_source_files
        )
        self.source_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.target_list = FileListFrame(
            lists_container,
            title="2. 대조 대상 파일 (선택)",
            on_add=self.add_target_files,
        )
        self.target_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.log_view = LogFrame(main_container)
        self.log_view.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        btn_container = ttk.Frame(main_container)
        btn_container.pack(fill=tk.X, pady=(0, 15))

        self.clean_btn = ttk.Button(
            btn_container,
            text="주소록 정리 시작",
            style="Accent.TButton",
            command=self.start_cleaning,
        )
        self.clean_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)

        self.compare_btn = ttk.Button(
            btn_container,
            text="데이터 대조 시작",
            command=self.start_comparison,
        )
        self.compare_btn.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=5
        )

        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill=tk.X)

        self.legend = StatusLegend(bottom_frame)
        self.legend.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        self.progress = ProgressFrame(bottom_frame)
        self.progress.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_label = ttk.Label(
            self, text="v1.1.4", font=self.version_font, foreground="#888888"
        )
        v_label.place(relx=1.0, rely=1.0, x=-10, y=-5, anchor="se")

    def add_source_files(self):
        filenames = filedialog.askopenfilenames(
            title="원본 파일 선택", filetypes=[("지원 파일", "*.csv *.xlsx *.xls")]
        )
        if filenames:
            self.source_list.add_files(list(filenames))
            self.log_view.log(f"정리할 파일 {len(filenames)}개가 추가되었습니다.")

    def add_target_files(self):
        filenames = filedialog.askopenfilenames(
            title="대조 대상 선택", filetypes=[("지원 파일", "*.csv *.xlsx *.xls")]
        )
        if filenames:
            self.target_list.add_files(list(filenames))
            self.log_view.log(f"대조 대상 파일 {len(filenames)}개가 추가되었습니다.")

    def start_cleaning(self):
        files = self.source_list.get_files()
        if not files:
            messagebox.showwarning("경고", "정리할 원본 파일을 선택해주세요.")
            return

        self._lock_ui()
        self.log_view.log("주소록 정리 작업을 시작합니다...", "INFO")

        thread = threading.Thread(target=self._clean_thread, args=(files,), daemon=True)
        thread.start()

    def start_comparison(self):
        source_files = self.source_list.get_files()
        target_files = self.target_list.get_files()

        if not source_files:
            messagebox.showwarning("경고", "대조할 원본 파일을 선택해주세요.")
            return
        if not target_files:
            messagebox.showwarning("경고", "대조 대상 파일(우측)을 선택해주세요.")
            return

        self._lock_ui()
        self.log_view.log("데이터 대조 작업을 시작합니다...", "INFO")

        thread = threading.Thread(
            target=self._compare_thread, args=(source_files, target_files), daemon=True
        )
        thread.start()

    def _lock_ui(self):
        self.clean_btn.configure(state="disabled")
        self.compare_btn.configure(state="disabled")
        self.progress.reset()
        self.log_view.clear()

    def _unlock_ui(self):
        self.clean_btn.configure(state="normal")
        self.compare_btn.configure(state="normal")

    def _clean_thread(self, files):
        try:
            self.after(
                0, self.log_view.log, f"{len(files)}개 파일 변환 시작...", "INFO"
            )
            self.after(0, self.progress.update_progress, 1, 1, "변환 중...")

            all_transformed = []
            for file_path in files:
                processor = ContactProcessor(str(file_path))
                result = processor.process()
                for row in result.comparison_data:
                    if row["변환됨"]:
                        all_transformed.append(
                            {"이름": row["이름"], "변환됨": row["변환됨"]}
                        )

            merged_data = self._merge_and_deduplicate(all_transformed, [])

            output_path = create_output_structure("병합", "변환")
            save_styled_excel(merged_data, output_path)

            self.after(
                0, self.log_view.log, f"변환 완료: {len(merged_data)}개 항목", "SUCCESS"
            )
            self.after(0, lambda: self.source_list.clear_all())
            self.after(0, self._on_complete)
        except Exception as e:
            self.after(0, self.log_view.log, f"정리 중 오류: {str(e)}", "ERROR")
            self.after(0, self._unlock_ui)

    def _compare_thread(self, source_files, target_files):
        try:
            self.after(
                0, self.log_view.log, "대조 대상 파일을 변환 중입니다...", "INFO"
            )
            self.after(0, self.progress.update_progress, 1, 2, "변환 중...")

            reference_transformed = self._process_reference_files(target_files)
            self.after(
                0,
                self.log_view.log,
                f"대조 대상 변환 완료 ({len(reference_transformed)}개)",
                "INFO",
            )

            self.after(0, self.progress.update_progress, 2, 2, "병합 중...")

            all_source = []
            for file_path in source_files:
                processor = ContactProcessor(str(file_path))
                result = processor.process()
                for row in result.comparison_data:
                    if row["변환됨"]:
                        all_source.append(
                            {"이름": row["이름"], "변환됨": row["변환됨"]}
                        )

            merged_data = self._merge_and_deduplicate(all_source, reference_transformed)

            output_path = create_output_structure("병합", "대조")
            save_styled_excel(merged_data, output_path)

            stats = {"O": 0, "△": 0, "X": 0}
            for row in merged_data:
                status = row.get("검증", "")
                if status in stats:
                    stats[status] += 1

            self.after(
                0,
                self.log_view.log,
                f"대조 완료 (O:{stats['O']}, △:{stats['△']}, X:{stats['X']})",
                "SUCCESS",
            )

            self.after(0, lambda: self.source_list.clear_all())
            self.after(0, lambda: self.target_list.clear_all())
            self.after(0, self._on_complete)
        except Exception as e:
            self.after(0, self.log_view.log, f"대조 중 오류: {str(e)}", "ERROR")
            self.after(0, self._unlock_ui)

    def _process_reference_files(self, target_files) -> list[dict]:
        transformed = []
        for f_path in target_files:
            processor = ContactProcessor(str(f_path))
            result = processor.process()
            for row in result.comparison_data:
                if row["변환됨"]:
                    transformed.append({"이름": row["이름"], "변환됨": row["변환됨"]})
        return transformed

    def _merge_and_deduplicate(
        self, left_data: list[dict], right_data: list[dict]
    ) -> list[dict]:
        import re
        
        def clean_name(name: str) -> str:
            name = name.strip()
            name = re.sub(r'[\d\-\+\(\)\s]+', '', name)
            return name
        
        result = []
        matched_right_indices = set()

        for idx, left_item in enumerate(left_data):
            left_name = left_item["이름"].strip()
            left_phone = left_item["변환됨"]
            left_name_clean = clean_name(left_name)

            name_match_found = False
            phone_match_indices = []

            for right_idx, right_item in enumerate(right_data):
                right_name = right_item["이름"].strip()
                right_phone = right_item["변환됨"]

                if left_phone == right_phone:
                    right_name_clean = clean_name(right_name)
                    if (
                        left_name_clean and right_name_clean and 
                        (left_name_clean in right_name_clean or right_name_clean in left_name_clean)
                    ):
                        result.append(
                            {
                                "이름": right_name,
                                "원본 전화번호": "",
                                "변환됨": right_phone,
                                "검증": "O",
                            }
                        )
                        matched_right_indices.add(right_idx)
                        name_match_found = True
                        break
                    else:
                        phone_match_indices.append(right_idx)

            if name_match_found:
                continue

            if phone_match_indices:
                result.append(
                    {
                        "이름": left_name,
                        "원본 전화번호": "",
                        "변환됨": left_phone,
                        "검증": "△",
                    }
                )
                for right_idx in phone_match_indices:
                    right_item = right_data[right_idx]
                    result.append(
                        {
                            "이름": right_item["이름"].strip(),
                            "원본 전화번호": "",
                            "변환됨": right_item["변환됨"],
                            "검증": "△",
                        }
                    )
                    matched_right_indices.add(right_idx)
            else:
                result.append(
                    {
                        "이름": left_name,
                        "원본 전화번호": "",
                        "변환됨": left_phone,
                        "검증": "X",
                    }
                )

        for right_idx, right_item in enumerate(right_data):
            if right_idx not in matched_right_indices:
                result.append(
                    {
                        "이름": right_item["이름"].strip(),
                        "원본 전화번호": "",
                        "변환됨": right_item["변환됨"],
                        "검증": "X",
                    }
                )

        return result

    def _load_reference_data(self, target_files) -> tuple[dict, list]:
        from contact_cleaner.core.normalizer import normalize_phone_number
        import csv
        import openpyxl

        phone_to_names = {}
        all_rows = []

        for f_path in target_files:
            path = Path(f_path)
            rows = []
            if path.suffix.lower() in [".xlsx", ".xls"]:
                wb = openpyxl.load_workbook(f_path, read_only=True, data_only=True)
                ws = wb.active
                if ws:
                    for row in ws.iter_rows(values_only=True):
                        if row and len(row) >= 2:
                            name_val = str(row[0]) if row[0] else ""
                            phone_val = str(row[1]) if row[1] else ""
                            rows.append((name_val, phone_val))
                            all_rows.append({"이름": name_val, "전화번호": phone_val})
                wb.close()
            else:
                for enc in ["utf-8", "cp949", "utf-8-sig"]:
                    try:
                        with open(f_path, "r", encoding=enc) as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if len(row) >= 2:
                                    rows.append((row[0], row[1]))
                                    all_rows.append(
                                        {"이름": row[0], "전화번호": row[1]}
                                    )
                        break
                    except:
                        continue

            for name_val, phone_val in rows:
                res = normalize_phone_number(phone_val)
                if res.status == "valid":
                    normalized = res.normalized
                    if normalized not in phone_to_names:
                        phone_to_names[normalized] = set()
                    phone_to_names[normalized].add(name_val.strip())

        return phone_to_names, all_rows

    def _apply_custom_comparison(self, result, reference_data: dict):
        new_comparison = []
        new_stats = {"O": 0, "이름": 0, "번호": 0, "X": 0, "△": 0}

        for row in result.comparison_data:
            name = row["이름"]
            trans = row["변환됨"]

            if not trans:
                status = "△"
            else:
                name_clean = name.strip().replace(" ", "")
                phone_match = trans in reference_data
                name_match = False

                if phone_match:
                    ref_names = reference_data[trans]
                    for ref_name in ref_names:
                        ref_name_clean = ref_name.replace(" ", "")
                        if name_clean in ref_name_clean or ref_name_clean in name_clean:
                            name_match = True
                            break

                if phone_match and name_match:
                    status = "O"
                elif name_match:
                    status = "이름"
                elif phone_match:
                    status = "번호"
                else:
                    status = "X"

            new_comparison.append(
                {
                    "이름": name,
                    "원본 전화번호": row["원본 전화번호"],
                    "변환됨": trans,
                    "검증": status,
                }
            )
            new_stats[status] += 1

        return result._replace(comparison_data=new_comparison, stats=new_stats)

    def _merge_with_reference(
        self, source_data: list[dict], reference_rows: list[dict]
    ) -> list[dict]:
        merged = []

        for row in source_data:
            merged.append(row)

        for ref_row in reference_rows:
            merged.append(
                {
                    "이름": ref_row["이름"],
                    "원본 전화번호": ref_row["전화번호"],
                    "변환됨": "",
                    "검증": "",
                }
            )

        return merged

    def _on_complete(self):
        self.progress.complete()
        self._unlock_ui()

        ans = messagebox.askyesno(
            "완료", "모든 파일 처리가 완료되었습니다.\n결과 폴더를 여시겠습니까?"
        )
        if ans:
            work_folder = get_work_folder()
            open_folder_in_explorer(work_folder)


if __name__ == "__main__":
    app = ContactCleanerApp()
    app.mainloop()
