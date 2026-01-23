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

        self.tk.call('tk', 'scaling', scale_factor * 1.125)

        # Calculate window size based on screen resolution
        screen_height = self.winfo_screenheight()
        
        # Base size for 1080p, scale up for higher resolutions
        if screen_height >= 2160:
            win_width = 1200
            win_height = 1000
        elif screen_height >= 1440:
            win_width = 1150
            win_height = 950
        else:
            win_width = 1150
            win_height = 950

        self.title("주소록 정리 v1.3.0")
        self.geometry(f"{win_width}x{win_height}")
        self.minsize(1000, 850)
        self.resizable(True, True)
        
        # Store dimensions for layout calculations
        self._win_height = win_height

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
        
        # Custom action button style with green color
        style.configure('Action.TButton', font=('Malgun Gothic', 12, 'bold'))

        # Calculate notebook height based on window height
        self._notebook_height = int(self._win_height * 0.55)
        self._main_container = main_container

        self.notebook = ttk.Notebook(main_container, height=self._notebook_height)
        self.notebook.pack(fill=tk.X, pady=(0, 15))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._setup_clean_tab()
        self._setup_compare_tab()
        self._setup_merge_tab()
        self._setup_help_tab()

        # Bottom section container (log + progress) - will be hidden on help tab
        self.bottom_section = ttk.Frame(main_container)
        self.bottom_section.pack(fill=tk.BOTH, expand=True)

        self.log_view = LogFrame(self.bottom_section)
        self.log_view.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        bottom_frame = ttk.Frame(self.bottom_section)
        bottom_frame.pack(fill=tk.X)

        self.progress = ProgressFrame(bottom_frame)
        self.progress.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_label = ttk.Label(
            self, text="v1.3.0", font=self.version_font, foreground="#888888"
        )
        v_label.place(relx=1.0, rely=1.0, x=-10, y=-5, anchor="se")

    def _on_tab_changed(self, event):
        """Hide log/progress when on help tab"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 3:  # Help tab (0-indexed)
            self.bottom_section.pack_forget()
        else:
            # Ensure bottom_section is visible
            if not self.bottom_section.winfo_ismapped():
                self.bottom_section.pack(fill=tk.BOTH, expand=True)

    def _setup_clean_tab(self):
        clean_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(clean_tab, text="Step 1. 정리")

        # Warning notice about required column headers
        info_frame = ttk.Frame(clean_tab)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = ttk.Label(
            info_frame,
            text='원본 파일에 "이름", "휴대폰번호" 또는 "성", "이름", "Mobile Phone" 등의\n컬럼 헤더가 포함되어 있어야 합니다.',
            foreground="#FF6600",
            font=self.small_font,
            justify=tk.LEFT
        )
        info_text.pack(anchor=tk.W)

        self.source_list = FileListFrame(
            clean_tab, title="정리할 원본 파일", on_add=self.add_source_files
        )
        self.source_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.clean_btn = ttk.Button(
            clean_tab,
            text="▶ 주소록 정리 시작",
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

        # Legend shown only in compare tab
        self.legend = StatusLegend(compare_tab)
        self.legend.pack(fill=tk.X, pady=(0, 10))

        # Options for comparison
        options_frame = ttk.Frame(compare_tab)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.hide_x_var = tk.BooleanVar(value=False)
        self.hide_x_cb = ttk.Checkbutton(
            options_frame, 
            text="대조 결과에서 'X(매칭 없음)' 항목 제외하고 저장", 
            variable=self.hide_x_var
        )
        self.hide_x_cb.pack(side=tk.LEFT)

        self.compare_btn = ttk.Button(
            compare_tab,
            text="▶ 데이터 대조 시작",
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
            text="▶ 병합 시작",
            style="Accent.TButton",
            command=self.start_merge,
        )
        self.merge_btn.pack(fill=tk.X, ipady=5)

    def _setup_help_tab(self):
        help_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(help_tab, text="도움말")

        # Scrollable text widget for help content
        help_frame = ttk.Frame(help_tab)
        help_frame.pack(fill=tk.BOTH, expand=True)

        help_text = tk.Text(
            help_frame,
            wrap=tk.WORD,
            font=("Malgun Gothic", 11),
            bd=0,
            highlightthickness=1,
            cursor="arrow",
            padx=15,
            pady=15,
        )
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(help_frame, orient="vertical", command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.config(yscrollcommand=scrollbar.set)

        # Configure text tags for formatting
        help_text.tag_configure("title", font=("Malgun Gothic", 16, "bold"), spacing3=10)
        help_text.tag_configure("section", font=("Malgun Gothic", 13, "bold"), spacing1=15, spacing3=5, foreground="#1976D2")
        help_text.tag_configure("subsection", font=("Malgun Gothic", 12, "bold"), spacing1=10, spacing3=3)
        help_text.tag_configure("normal", font=("Malgun Gothic", 11), spacing1=2, lmargin1=20, lmargin2=20)
        help_text.tag_configure("bullet", font=("Malgun Gothic", 11), spacing1=2, lmargin1=30, lmargin2=40)
        help_text.tag_configure("warning", font=("Malgun Gothic", 11), foreground="#F44336", lmargin1=20, lmargin2=20)
        help_text.tag_configure("info", font=("Malgun Gothic", 11), foreground="#2196F3", lmargin1=20, lmargin2=20)

        # Help content
        help_content = [
            ("title", "주소록 정리 v1.3.0 사용 매뉴얼\n\n"),
            
            ("section", "1. Step 1. 정리 (주소록 정리)\n"),
            ("normal", "원본 주소록 파일의 전화번호를 정규화하고 중복을 제거합니다.\n\n"),
            ("subsection", "사용 방법:\n"),
            ("bullet", "• 정리할 원본 파일을 드래그하거나 '파일 추가' 버튼으로 선택\n"),
            ("bullet", "• CSV, XLSX, XLS 파일 형식 지원\n"),
            ("bullet", "• '▶ 주소록 정리 시작' 버튼 클릭\n"),
            ("bullet", "• 결과 파일이 바탕화면 > 주소록정리결과 폴더에 저장됨\n\n"),
            ("subsection", "중요 사항:\n"),
            ("warning", "• 파일의 첫 번째 행(헤더)에 '이름', '휴대폰번호' 등의 명칭이 포함되어야 자동 인식됩니다.\n"),
            ("warning", "• 인식 가능한 헤더 예: 성함, 성명, 이름, 전화번호, 연락처, Mobile, Phone 등\n"),
            ("bullet", "• 전화번호는 010-XXXX-XXXX 형식으로 자동 변환됩니다.\n\n"),
            ("subsection", "출력 형식:\n"),
            ("bullet", "• 연번, 이름, 휴대폰번호, 추천1~3, 선택병합, 휴대폰 저장파일명\n\n"),

            ("section", "2. Step 2. 대조 (주소록 비교)\n"),
            ("normal", "두 주소록을 비교하여 일치 여부를 확인합니다.\n\n"),
            ("subsection", "사용 방법:\n"),
            ("bullet", "• '비교할 주소록': 기준이 되는 주소록 파일 선택\n"),
            ("bullet", "• '대조 대상 파일': 비교할 대상 주소록 파일 선택\n"),
            ("bullet", "• '데이터 대조 시작' 버튼 클릭\n\n"),
            ("subsection", "대조 옵션:\n"),
            ("bullet", "• 'X(매칭 없음) 항목 제외': 결과 파일에서 일치하지 않는 데이터는 저장하지 않습니다.\n"),
            ("info", "  (비교 주소록에 없는 새로운 연락처만 필터링하고 싶을 때 유용합니다)\n\n"),
            ("subsection", "대조 결과 상태:\n"),
            ("bullet", "• O: 이름과 번호가 모두 일치\n"),
            ("bullet", "• △(번호): 번호만 일치 (이름이 다름)\n"),
            ("bullet", "• △(이름): 이름만 일치 (번호가 다름)\n"),
            ("bullet", "• X: 일치하는 항목 없음\n\n"),

            ("section", "3. Step 3. 병합 (선택 병합)\n"),
            ("normal", "여러 주소록에서 선택한 항목만 모아서 최종적으로 하나의 파일로 병합합니다.\n\n"),
            ("subsection", "사용 방법:\n"),
            ("bullet", "• 정리 또는 대조 결과 파일(엑셀)을 열어 '선택병합' 열에 'O' 표시를 합니다.\n"),
            ("info", "  (대문자 'O', 소문자 'o', 한글 'ㅇ', 체크 표시 등 모두 가능)\n"),
            ("bullet", "• 파일명을 '{소유자명}_주소록.xlsx' 형식으로 변경합니다.\n"),
            ("info", "  예: 홍길동_주소록.xlsx, 김철수_주소록.xlsx\n"),
            ("bullet", "• 수정된 파일들을 드래그하여 추가하고 '▶ 병합 시작' 클릭\n\n"),
            ("subsection", "병합 규칙:\n"),
            ("bullet", "• '선택병합'에 표시된 항목만 최종 결과에 포함됩니다.\n"),
            ("bullet", "• 동일한 (이름, 번호) 쌍은 중복으로 간주하여 한 번만 포함됩니다.\n"),
            ("bullet", "• 결과 파일에는 주소록의 원래 주인이 누구인지 '주소록 소유자명' 컬럼이 추가됩니다.\n\n"),

            ("section", "4. 지원 파일 형식\n"),
            ("bullet", "• CSV (쉼표로 구분된 파일)\n"),
            ("bullet", "• XLSX (Excel 2007 이상)\n"),
            ("bullet", "• XLS (Excel 97-2003)\n"),
            ("normal", "\n인코딩: UTF-8, CP949(한글 Windows) 자동 감지\n\n"),

            ("section", "5. 자주 발생하는 오류 및 해결 방법\n\n"),
            
            ("subsection", "❌ '파일명 형식 오류'\n"),
            ("warning", "원인: 병합 시 파일명이 '{이름}_주소록.xlsx' 형식이 아님\n"),
            ("normal", "해결: 파일명을 '홍길동_주소록.xlsx' 형식으로 변경\n\n"),
            
            ("subsection", "❌ '정리할 원본 파일을 선택해주세요'\n"),
            ("warning", "원인: 파일을 선택하지 않고 시작 버튼을 클릭\n"),
            ("normal", "해결: 먼저 파일을 추가한 후 시작 버튼 클릭\n\n"),
            
            ("subsection", "❌ '병합할 데이터가 없습니다'\n"),
            ("warning", "원인: 선택병합 열에 O 표시된 항목이 없음\n"),
            ("normal", "해결: 병합하려는 파일에서 선택병합 열에 O 표시 후 저장\n\n"),
            
            ("subsection", "❌ 전화번호가 이상하게 변환됨\n"),
            ("warning", "원인: 원본 파일의 전화번호 형식이 올바르지 않음\n"),
            ("normal", "해결: 전화번호가 숫자로만 구성되어 있는지 확인\n"),
            ("normal", "      앞에 '(국가번호)' 등이 붙어 있으면 제거\n\n"),
            
            ("subsection", "❌ 파일을 읽을 수 없음\n"),
            ("warning", "원인: 파일이 다른 프로그램에서 열려 있음\n"),
            ("normal", "해결: Excel에서 파일을 닫고 다시 시도\n\n"),

            ("section", "6. 결과 파일 위치\n"),
            ("normal", "모든 결과 파일은 아래 경로에 저장됩니다:\n"),
            ("info", "바탕화면 > 주소록정리결과 > [날짜] > [시간]\n\n"),
            
            ("section", "7. 팁\n"),
            ("bullet", "• 로그 메시지의 파일명을 클릭하면 파일이 열립니다\n"),
            ("bullet", "• 여러 파일을 한번에 드래그하여 추가할 수 있습니다\n"),
            ("bullet", "• 작업 완료 후 결과 폴더 열기 대화상자가 나타납니다\n"),
        ]

        for tag, text in help_content:
            help_text.insert(tk.END, text, tag)

        help_text.config(state=tk.DISABLED)

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
            # Simple dedup for clean - no comparison logic needed
            merged_data = self._simple_deduplicate(all_transformed)

            def on_save_progress(current, total):
                pct = int((current / total) * 100) if total > 0 else 0
                self.after(0, self.progress.update_progress, pct, 100, "저장 중")

            output_path = create_output_structure("정리")
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

            hide_x = self.hide_x_var.get()

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

            if hide_x:
                original_count = len(merged_data)
                merged_data = [row for row in merged_data if row.get("검증") != "X"]
                self.after(0, self.log_view.log, f"'X' 항목 {original_count - len(merged_data)}개를 제외했습니다.", "INFO")

            def on_save_progress(current, total):
                pct = int((current / total) * 100) if total > 0 else 0
                self.after(0, self.progress.update_progress, pct, 100, "저장 중")

            output_path = create_output_structure("대조")
            save_styled_excel(merged_data, output_path,
                              progress_callback=on_save_progress)

            stats = {"O": 0, "△(번호)": 0, "△(이름)": 0, "X": 0}
            for row in merged_data:
                status = row.get("검증", "")
                if status in stats:
                    stats[status] += 1

            self.after(0, self.progress.update_progress, 100, 100, "완료")
            self.after(0, self.log_view.log,
                       f"대조 완료 (O:{stats['O']}, △(번호):{stats['△(번호)']}, △(이름):{stats['△(이름)']}, X:{stats['X']})", "SUCCESS", str(output_path))
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

            output_path = create_output_structure("최종병합")
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
                # Find the first item where checked=True instead of always using items[0]
                checked_item = next((item for item in items if item["checked"]), items[0])
                result.append(checked_item)

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

    def _simple_deduplicate(self, data: list[dict]) -> list[dict]:
        """Simple deduplication by phone only - for clean function only"""
        seen = set()
        result = []
        for item in data:
            name = (item.get("이름") or "").strip()
            phone = item.get("변환됨", "")
            key = phone  # Deduplicate by phone only, keep first occurrence
            if key not in seen:
                seen.add(key)
                result.append({
                    "이름": name,
                    "변환됨": phone,
                    "검증": "",  # Empty for clean results
                })
        return result

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

        # Build phone index for right data
        right_by_phone: dict[str, list[tuple[int, dict]]] = {}
        for idx, item in enumerate(right_data):
            phone = item["변환됨"]
            if phone not in right_by_phone:
                right_by_phone[phone] = []
            right_by_phone[phone].append((idx, item))

        # Build name index for right data (for name-only matching)
        right_by_name: dict[str, list[tuple[int, dict]]] = {}
        for idx, item in enumerate(right_data):
            name_clean = clean_name(item["이름"])
            if name_clean:
                if name_clean not in right_by_name:
                    right_by_name[name_clean] = []
                right_by_name[name_clean].append((idx, item))

        result = []
        matched_right_indices = set()

        for left_item in left_data:
            left_name = left_item["이름"].strip() if left_item["이름"] else ""
            left_phone = left_item["변환됨"]
            left_name_clean = clean_name(left_name)

            phone_candidates = right_by_phone.get(left_phone, [])
            available_phone = [(idx, item) for idx,
                         item in phone_candidates if idx not in matched_right_indices]

            # Check for exact match (name AND phone)
            exact_match_found = False
            for right_idx, right_item in available_phone:
                right_name = right_item["이름"].strip() if right_item["이름"] else ""
                right_name_clean = clean_name(right_name)

                if left_name_clean and right_name_clean:
                    if left_name_clean == right_name_clean:
                        result.append({
                            "이름": right_name,
                            "원본 전화번호": "",
                            "변환됨": left_phone,
                            "검증": "O",
                        })
                        matched_right_indices.add(right_idx)
                        exact_match_found = True
                        break

            if exact_match_found:
                continue

            # Check for phone-only match
            if available_phone:
                right_idx, right_item = available_phone[0]
                result.append({
                    "이름": left_name,
                    "원본 전화번호": "",
                    "변환됨": left_phone,
                    "검증": "△(번호)",
                })
                matched_right_indices.add(right_idx)
                continue

            # Check for name-only match
            if left_name_clean:
                name_match_found = False
                for name_key, name_candidates in right_by_name.items():
                    if left_name_clean == name_key:
                        available_name = [(idx, item) for idx, item in name_candidates 
                                         if idx not in matched_right_indices]
                        if available_name:
                            right_idx, right_item = available_name[0]
                            result.append({
                                "이름": left_name,
                                "원본 전화번호": "",
                                "변환됨": left_phone,
                                "검증": "△(이름)",
                            })
                            matched_right_indices.add(right_idx)
                            name_match_found = True
                            break
                if name_match_found:
                    continue

            # No match at all
            result.append({
                "이름": left_name,
                "원본 전화번호": "",
                "변환됨": left_phone,
                "검증": "X",
            })

        # Do NOT add unmatched right items - comparison should only output left_data items
        
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
