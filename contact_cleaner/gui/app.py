from contact_cleaner.gui.widgets import (
    FileListFrame,
    StatusLegend,
    ProgressFrame,
    LogFrame,
)
from contact_cleaner.gui.theme import init_theme
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))


try:
    from tkinterdnd2 import TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# Use TkinterDnD.Tk if available, otherwise fallback to standard tk.Tk
BaseClass = TkinterDnD.Tk if HAS_DND else tk.Tk


class ContactCleanerApp(BaseClass):
    def __init__(self):
        super().__init__()

        self.withdraw()

        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        init_theme(self)

        try:
            from ctypes import windll
            dpi = windll.user32.GetDpiForSystem()
            scale_factor = dpi / 96.0
        except:
            scale_factor = 1.0

        self.tk.call('tk', 'scaling', scale_factor * 1.25)

        self.title("주소록 정리 v1.3.0")
        self.geometry("1150x1150")
        self.minsize(1150, 1150)
        self.maxsize(1150, 1150)
        self.resizable(False, False)

        self._setup_ui()

        self.update_idletasks()
        self.deiconify()

    def _setup_ui(self):
        from tkinter import font as tkfont

        self.header_font = tkfont.Font(
            family="Malgun Gothic", size=24, weight="bold")
        self.default_font_bold = tkfont.Font(
            family="Malgun Gothic", size=12, weight="bold"
        )
        self.small_font = tkfont.Font(family="Malgun Gothic", size=11)
        self.version_font = tkfont.Font(family="Malgun Gothic", size=10)

        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[
                        20, 10], font=('Malgun Gothic', 12))
        style.configure('TButton', font=('Malgun Gothic', 12))
        style.configure('Accent.TButton', font=('Malgun Gothic', 12))
        style.configure('TLabelframe.Label', font=(
            'Malgun Gothic', 13, 'bold'))
        style.configure('TLabel', font=('Malgun Gothic', 12))
        style.configure('TProgressbar', thickness=100)

        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self._setup_clean_tab()
        self._setup_compare_tab()
        self._setup_merge_tab()

        self.log_view = LogFrame(main_container)
        self.log_view.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill=tk.X)

        self.legend = StatusLegend(bottom_frame)
        self.legend.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        self.progress = ProgressFrame(bottom_frame)
        self.progress.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_label = ttk.Label(
            self, text="v1.3.0", font=self.version_font, foreground="#888888"
        )
        v_label.place(relx=1.0, rely=1.0, x=-10, y=-5, anchor="se")

    def _setup_clean_tab(self):
        clean_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(clean_tab, text="Step 1. 정리")

        self.source_list = FileListFrame(
            clean_tab, title="정리할 원본 파일", on_add=self.add_source_files
        )
        self.source_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.clean_btn = ttk.Button(
            clean_tab,
            text="주소록 정리 시작",
            style="Accent.TButton",
            command=self.start_cleaning,
        )
        self.clean_btn.pack(fill=tk.X, ipady=5)

    def _setup_compare_tab(self):
        compare_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(compare_tab, text="Step 2. 대조")

        lists_container = ttk.Frame(compare_tab)
        lists_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.compare_source_list = FileListFrame(
            lists_container, title="비교할 주소록", on_add=self.add_compare_source_files
        )
        self.compare_source_list.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.target_list = FileListFrame(
            lists_container,
            title="대조 대상 파일",
            on_add=self.add_target_files,
        )
        self.target_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.compare_btn = ttk.Button(
            compare_tab,
            text="데이터 대조 시작",
            style="Accent.TButton",
            command=self.start_comparison,
        )
        self.compare_btn.pack(fill=tk.X, ipady=5)

    def _setup_merge_tab(self):
        merge_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(merge_tab, text="Step 3. 병합")

        info_frame = ttk.Frame(merge_tab)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = ttk.Label(
            info_frame,
            text='파일명을 "{주소록 소유자명}_주소록.xlsx" 형식으로 수정하세요!\n예: 홍길동_주소록.xlsx',
            foreground="#FF6600",
            font=self.small_font,
            justify=tk.LEFT
        )
        info_text.pack(anchor=tk.W)

        notice_text = ttk.Label(
            info_frame,
            text='선택 시 대조 또는 정리한 파일의 "선택병합" 셀에 O(알파벳 O) 표시해주세요.',
            foreground="#0066CC",
            font=self.small_font,
            justify=tk.LEFT
        )
        notice_text.pack(anchor=tk.W, pady=(5, 0))

        self.merge_list = FileListFrame(
            merge_tab, title="병합할 파일 목록", on_add=self.add_merge_files
        )
        self.merge_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.merge_btn = ttk.Button(
            merge_tab,
            text="병합 시작",
            style="Accent.TButton",
            command=self.start_merge,
        )
        self.merge_btn.pack(fill=tk.X, ipady=5)

    def add_source_files(self):
        filenames = filedialog.askopenfilenames(
            title="원본 파일 선택", filetypes=[("지원 파일", "*.csv *.xlsx *.xls")]
        )
        if filenames:
            self.source_list.add_files(list(filenames))
            self.log_view.log(f"정리할 파일 {len(filenames)}개가 추가되었습니다.")

    def add_compare_source_files(self):
        filenames = filedialog.askopenfilenames(
            title="원본 파일 선택", filetypes=[("지원 파일", "*.csv *.xlsx *.xls")]
        )
        if filenames:
            self.compare_source_list.add_files(list(filenames))
            self.log_view.log(f"대조할 파일 {len(filenames)}개가 추가되었습니다.")

    def add_target_files(self):
        filenames = filedialog.askopenfilenames(
            title="대조 대상 선택", filetypes=[("지원 파일", "*.csv *.xlsx *.xls")]
        )
        if filenames:
            self.target_list.add_files(list(filenames))
            self.log_view.log(f"대조 대상 파일 {len(filenames)}개가 추가되었습니다.")

    def add_merge_files(self):
        filenames = filedialog.askopenfilenames(
            title="병합할 파일 선택", filetypes=[("Excel 파일", "*.xlsx *.xls")]
        )
        if filenames:
            self.merge_list.add_files(list(filenames))
            self.log_view.log(f"병합 파일 {len(filenames)}개가 추가되었습니다.")

    def start_cleaning(self):
        files = self.source_list.get_files()
        if not files:
            self.log_view.log("정리할 원본 파일을 선택해주세요.", "WARNING")
            return

        self._lock_ui()
        self.log_view.log("주소록 정리 작업을 시작합니다", "INFO")

        thread = threading.Thread(
            target=self._clean_thread, args=(files,), daemon=True)
        thread.start()

    def start_comparison(self):
        source_files = self.compare_source_list.get_files()
        target_files = self.target_list.get_files()

        if not source_files:
            self.log_view.log("대조할 원본 파일을 선택해주세요.", "WARNING")
            return
        if not target_files:
            self.log_view.log("대조 대상 파일을 선택해주세요.", "WARNING")
            return

        self._lock_ui()
        self.log_view.log("데이터 대조 작업을 시작합니다", "INFO")

        thread = threading.Thread(
            target=self._compare_thread, args=(
                source_files, target_files), daemon=True
        )
        thread.start()

    def start_merge(self):
        merge_files = self.merge_list.get_files()

        if not merge_files:
            self.log_view.log("병합할 파일을 선택해주세요.", "WARNING")
            return

        self._lock_ui()
        self.log_view.log("병합 작업을 시작합니다.", "INFO")

        thread = threading.Thread(
            target=self._merge_thread, args=(merge_files,), daemon=True
        )
        thread.start()

    def _lock_ui(self):
        self.clean_btn.configure(state="disabled")
        self.compare_btn.configure(state="disabled")
        self.merge_btn.configure(state="disabled")
        self.progress.reset()

    def _unlock_ui(self):
        self.clean_btn.configure(state="normal")
        self.compare_btn.configure(state="normal")
        self.merge_btn.configure(state="normal")

    def _clean_thread(self, files):
        from contact_cleaner.core.processor import ContactProcessor
        from contact_cleaner.utils.file_utils import (
            create_output_structure,
            save_styled_excel,
        )
        try:
            self.after(0, self.log_view.log, f"{len(files)}개 파일 변환 시작", "INFO")
            self.after(0, self.progress.update_progress, 0, 100, "파일 읽는 중")

            all_transformed = []
            for file_path in files:
                processor = ContactProcessor(str(file_path))
                result = processor.process()
                for row in result.comparison_data:
                    if row["변환됨"]:
                        all_transformed.append(
                            {"이름": row["이름"], "변환됨": row["변환됨"]}
                        )

            self.after(0, self.progress.update_progress, 0, 100, "중복 제거 중")
            merged_data = self._merge_and_deduplicate(all_transformed, [])
            for item in merged_data:
                item["검증"] = ""

            def on_save_progress(current, total):
                pct = int((current / total) * 100) if total > 0 else 0
                self.after(0, self.progress.update_progress, pct, 100, "저장 중")

            output_path = create_output_structure("병합", "변환")
            save_styled_excel(merged_data, output_path,
                              progress_callback=on_save_progress)

            self.after(0, self.progress.update_progress, 100, 100, "완료")
            self.after(0, self.log_view.log,
                       f"변환 완료: {len(merged_data)}개 항목", "SUCCESS", str(output_path))
            self.after(0, lambda: self.source_list.clear_all())
            self.after(0, self._on_complete)
        except Exception as e:
            self.after(0, self.log_view.log, f"정리 중 오류: {str(e)}", "ERROR")
            self.after(0, self._unlock_ui)

    def _compare_thread(self, source_files, target_files):
        from contact_cleaner.core.processor import ContactProcessor
        from contact_cleaner.utils.file_utils import (
            create_output_structure,
            save_styled_excel,
        )
        try:
            self.after(0, self.log_view.log, "대조 대상 파일을 변환 중입니다", "INFO")
            self.after(0, self.progress.update_progress, 0, 100, "파일 읽는 중")

            reference_transformed = []
            for file_path in target_files:
                processor = ContactProcessor(str(file_path))
                result = processor.process()
                for row in result.transformed_data:
                    reference_transformed.append(
                        {"이름": row["이름"], "변환됨": row["변환됨"]})

            self.after(0, self.log_view.log,
                       f"대조 대상 변환 완료 ({len(reference_transformed)}개)", "INFO")

            all_source = []
            for file_path in source_files:
                processor = ContactProcessor(str(file_path))
                result = processor.process()
                for row in result.comparison_data:
                    if row["변환됨"]:
                        all_source.append({"이름": row["이름"], "변환됨": row["변환됨"]})

            self.after(0, self.progress.update_progress, 0, 100, "대조 중")
            merged_data = self._merge_and_deduplicate(
                all_source, reference_transformed)

            def on_save_progress(current, total):
                pct = int((current / total) * 100) if total > 0 else 0
                self.after(0, self.progress.update_progress, pct, 100, "저장 중")

            output_path = create_output_structure("병합", "대조")
            save_styled_excel(merged_data, output_path,
                              progress_callback=on_save_progress)

            stats = {"O": 0, "△": 0, "X": 0}
            for row in merged_data:
                status = row.get("검증", "")
                if status in stats:
                    stats[status] += 1

            self.after(0, self.progress.update_progress, 100, 100, "완료")
            self.after(0, self.log_view.log,
                       f"대조 완료 (O:{stats['O']}, △:{stats['△']}, X:{stats['X']})", "SUCCESS", str(output_path))
            self.after(0, lambda: self.source_list.clear_all())
            self.after(0, lambda: self.target_list.clear_all())
            self.after(0, self._on_complete)
        except Exception as e:
            self.after(0, self.log_view.log, f"대조 중 오류: {str(e)}", "ERROR")
            self.after(0, self._unlock_ui)

    def _merge_thread(self, merge_files):
        from contact_cleaner.utils.file_utils import create_output_structure
        import openpyxl
        try:
            self.after(0, self.log_view.log,
                       f"{len(merge_files)}개 파일 로드 중", "INFO")
            self.after(0, self.progress.update_progress, 0, 100, "파일 로드 중")

            all_data = []
            invalid_files = []

            for file_path in merge_files:
                try:
                    owner_name = self._extract_owner_name(file_path)
                    if not owner_name:
                        invalid_files.append(Path(file_path).name)
                        continue

                    wb = openpyxl.load_workbook(file_path)
                    ws = wb.active
                    if not ws:
                        continue

                    for row_idx in range(3, ws.max_row + 1):
                        name = ws.cell(row_idx, 2).value
                        phone = ws.cell(row_idx, 3).value
                        rec1 = ws.cell(row_idx, 4).value
                        rec2 = ws.cell(row_idx, 5).value
                        rec3 = ws.cell(row_idx, 6).value
                        rec4 = ws.cell(row_idx, 7).value
                        filename = ws.cell(row_idx, 8).value

                        if phone:
                            all_data.append({
                                "주소록 소유자명": owner_name,
                                "이름": name or "",
                                "변환됨": phone,
                                "추천1": rec1 or "",
                                "추천2": rec2 or "",
                                "추천3": rec3 or "",
                                "선택병합": rec4 or "",
                                "파일명": filename or ""
                            })
                    wb.close()
                except Exception as e:
                    self.after(
                        0, self.log_view.log, f"{Path(file_path).name} 로드 실패: {str(e)}", "WARNING")

            if invalid_files:
                self.after(0, self.log_view.log,
                           f"파일명 형식 오류: {', '.join(invalid_files)}", "WARNING")

            if not all_data:
                self.after(0, self.log_view.log, "병합할 데이터가 없습니다.", "ERROR")
                self.after(0, self._unlock_ui)
                return

            self.after(0, self.log_view.log,
                       f"총 {len(all_data)}개 항목 로드 완료", "INFO")
            self.after(0, self.progress.update_progress, 0, 100, "중복 제거 중")

            merged_data = self._merge_with_check(all_data)

            self.after(0, self.log_view.log,
                       f"중복 제거 후 {len(merged_data)}개 항목", "INFO")
            self.after(0, self.progress.update_progress, 0, 100, "파일 저장 중")

            output_path = create_output_structure("병합", "최종병합")
            self._save_merged_excel(merged_data, output_path)

            self.after(0, self.progress.update_progress, 100, 100, "완료")
            self.after(0, self.log_view.log,
                       f"병합 완료: {len(merged_data)}개 항목", "SUCCESS", str(output_path))
            self.after(0, lambda: self.merge_list.clear_all())
            self.after(0, self._on_complete)
        except Exception as e:
            self.after(0, self.log_view.log, f"병합 중 오류: {str(e)}", "ERROR")
            self.after(0, self._unlock_ui)

    def _extract_owner_name(self, file_path: str) -> str:
        import re
        filename = Path(file_path).stem
        match = re.search(r'([^_\s]+)[_\s]*주소록', filename)
        if match:
            return match.group(1)
        return ""

    def _merge_with_check(self, all_data: list[dict]) -> list[dict]:
        import re

        def is_checked(value) -> bool:
            if not value:
                return False
            value_str = str(value).strip().upper()
            return bool(re.match(r'^[OㅇVX✓✔CHECK]', value_str))

        merged = {}

        for item in all_data:
            phone = item["변환됨"]
            name = item["이름"]
            key = (name, phone)

            rec4_checked = is_checked(item.get("선택병합", ""))

            if key not in merged:
                merged[key] = []

            merged[key].append({
                "주소록 소유자명": item["주소록 소유자명"],
                "이름": name,
                "변환됨": phone,
                "추천1": item.get("추천1", ""),
                "추천2": item.get("추천2", ""),
                "추천3": item.get("추천3", ""),
                "선택병합": item.get("선택병합", ""),
                "파일명": item.get("파일명", ""),
                "checked": rec4_checked
            })

        result = []
        for key, items in merged.items():
            has_checked = any(item["checked"] for item in items)
            if has_checked:
                result.append(items[0])

        return result

    def _save_merged_excel(self, data: list[dict], path: Path) -> None:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        wb = openpyxl.Workbook()
        ws = wb.active
        if not ws:
            return

        ws.append(['*선택병합 시에는 (해당 열에 "O" 표시해 주세요.)'])

        headers = [
            "연번",
            "주소록 소유자명",
            "이름 (휴대폰에 저장될 이름)",
            "휴대폰번호",
            "추천1(DW)",
            "추천2",
            "추천3(비교대상과체크)",
            "선택병합",
            "휴대폰 저장파일명",
        ]
        ws.append(headers)

        gray_fill = PatternFill(start_color="D3D3D3",
                                end_color="D3D3D3", fill_type="solid")
        yellow_fill = PatternFill(
            start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        header_font = Font(name="Malgun Gothic", size=11, bold=False)
        header_font_red = Font(name="Malgun Gothic", size=11, bold=False, color="FF0000")
        center_alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        for col_idx in range(1, 10):
            cell = ws.cell(row=2, column=col_idx)
            if col_idx == 8:
                cell.font = header_font_red
            else:
                cell.font = header_font
            cell.alignment = center_alignment
            cell.border = thin_border
            cell.fill = gray_fill

        for idx, item in enumerate(data, start=1):
            current_row = idx + 2
            ws.cell(row=current_row, column=1, value=idx)
            ws.cell(row=current_row, column=2, value=item.get("주소록 소유자명", ""))
            ws.cell(row=current_row, column=3, value=item.get("이름", "") or " ")
            ws.cell(row=current_row, column=4,
                    value=item.get("변환됨", "") or " ")
            ws.cell(row=current_row, column=5, value=item.get("추천1", ""))
            ws.cell(row=current_row, column=6, value=item.get("추천2", ""))
            ws.cell(row=current_row, column=7, value=item.get("추천3", ""))
            ws.cell(row=current_row, column=8, value=item.get("선택병합", ""))
            ws.cell(row=current_row, column=9, value=item.get("파일명", ""))

            for col_idx in range(1, 10):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.border = thin_border
                cell.font = Font(name="Malgun Gothic", size=10)
                if col_idx in [1, 7]:
                    cell.alignment = center_alignment
                if col_idx == 7:
                    cell.fill = yellow_fill

        from openpyxl.utils import get_column_letter
        widths = {1: 8, 2: 15, 3: 30, 4: 20, 5: 10, 6: 10, 7: 25, 8: 10, 9: 25}
        for col_idx, width in widths.items():
            ws.column_dimensions[get_column_letter(col_idx)].width = width

        if path.suffix != ".xlsx":
            path = path.with_suffix(".xlsx")
        wb.save(path)

    def _process_reference_files(self, target_files) -> list[dict]:
        from contact_cleaner.core.processor import ContactProcessor
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
            if not name:
                return ""
            name = name.strip()
            name = re.sub(r'[\d\-\+\(\)\s]+', '', name)
            return name

        right_by_phone: dict[str, list[tuple[int, dict]]] = {}
        for idx, item in enumerate(right_data):
            phone = item["변환됨"]
            if phone not in right_by_phone:
                right_by_phone[phone] = []
            right_by_phone[phone].append((idx, item))

        result = []
        matched_right_indices = set()

        for left_item in left_data:
            left_name = left_item["이름"].strip() if left_item["이름"] else ""
            left_phone = left_item["변환됨"]
            left_name_clean = clean_name(left_name)

            candidates = right_by_phone.get(left_phone, [])
            available = [(idx, item) for idx,
                         item in candidates if idx not in matched_right_indices]

            if not available:
                result.append({
                    "이름": left_name,
                    "원본 전화번호": "",
                    "변환됨": left_phone,
                    "검증": "X",
                })
                continue

            name_match_found = False
            phone_only_matches = []

            for right_idx, right_item in available:
                right_name = right_item["이름"].strip(
                ) if right_item["이름"] else ""
                right_name_clean = clean_name(right_name)

                if left_name_clean and right_name_clean:
                    if left_name_clean in right_name_clean or right_name_clean in left_name_clean:
                        result.append({
                            "이름": right_name,
                            "원본 전화번호": "",
                            "변환됨": left_phone,
                            "검증": "O",
                        })
                        matched_right_indices.add(right_idx)
                        name_match_found = True
                        break
                    else:
                        phone_only_matches.append((right_idx, right_item))
                else:
                    merged_name = left_name or right_name
                    result.append({
                        "이름": merged_name,
                        "원본 전화번호": "",
                        "변환됨": left_phone,
                        "검증": "O",
                    })
                    matched_right_indices.add(right_idx)
                    name_match_found = True
                    break

            if name_match_found:
                continue

            if phone_only_matches:
                result.append({
                    "이름": left_name,
                    "원본 전화번호": "",
                    "변환됨": left_phone,
                    "검증": "△",
                })
                for right_idx, right_item in phone_only_matches:
                    result.append({
                        "이름": right_item["이름"].strip() if right_item["이름"] else "",
                        "원본 전화번호": "",
                        "변환됨": right_item["변환됨"],
                        "검증": "△",
                    })
                    matched_right_indices.add(right_idx)

        for idx, right_item in enumerate(right_data):
            if idx not in matched_right_indices:
                result.append({
                    "이름": right_item["이름"].strip() if right_item["이름"] else "",
                    "원본 전화번호": "",
                    "변환됨": right_item["변환됨"],
                    "검증": "X",
                })

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
                wb = openpyxl.load_workbook(
                    f_path, read_only=True, data_only=True)
                ws = wb.active
                if ws:
                    for row in ws.iter_rows(values_only=True):
                        if row and len(row) >= 2:
                            name_val = str(row[0]) if row[0] else ""
                            phone_val = str(row[1]) if row[1] else ""
                            rows.append((name_val, phone_val))
                            all_rows.append(
                                {"이름": name_val, "전화번호": phone_val})
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
        from contact_cleaner.utils.file_utils import get_work_folder, open_folder_in_explorer
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
