import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import List, Callable, Optional
from datetime import datetime


class FileListFrame(ttk.LabelFrame):
    def __init__(
        self, parent, title="선택된 파일", on_add: Optional[Callable] = None, **kwargs
    ):
        self.title_base = title
        super().__init__(parent, text=f"{self.title_base} (0개)", padding=10, **kwargs)
        self.files: List[str] = []
        self._listbox_font = tkfont.Font(family="Malgun Gothic", size=10)
        self._setup_ui(on_add)

    def _setup_ui(self, on_add):
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            height=6,
            bd=0,
            highlightthickness=1,
            relief="flat",
            font=self._listbox_font,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X)

        add_btn = ttk.Button(
            btn_frame, text="파일 추가", command=on_add, style="Accent.TButton"
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 5))

        del_btn = ttk.Button(btn_frame, text="제거", command=self.remove_selection)
        del_btn.pack(side=tk.LEFT)

    def add_files(self, new_files):
        for f in new_files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, f)
        self._update_label()

    def remove_selection(self):
        selection = self.listbox.curselection()
        for index in reversed(selection):
            self.listbox.delete(index)
            del self.files[index]
        self._update_label()

    def _update_label(self):
        self.configure(text=f"{self.title_base} ({len(self.files)}개)")

    def get_files(self) -> List[str]:
        return self.files

    def clear_all(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)
        self._update_label()


class LogFrame(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="로그 메시지", padding=10, **kwargs)
        self._log_font = tkfont.Font(family="Malgun Gothic", size=9)
        self._setup_ui()

    def _setup_ui(self):
        self.text_area = tk.Text(
            self,
            height=8,
            font=self._log_font,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bd=0,
            highlightthickness=1,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        # 색상 태그 설정
        self.text_area.tag_configure("INFO", foreground="#2196F3")
        self.text_area.tag_configure("SUCCESS", foreground="#4CAF50")
        self.text_area.tag_configure("WARNING", foreground="#FF9800")
        self.text_area.tag_configure("ERROR", foreground="#F44336")
        self.text_area.tag_configure("TIME", foreground="#888888")

    def log(self, message: str, level: str = "INFO"):
        self.text_area.config(state=tk.NORMAL)

        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.text_area.insert(tk.END, timestamp, "TIME")

        if level == "SUCCESS":
            self.text_area.insert(tk.END, "✓ ", "SUCCESS")
        elif level == "WARNING":
            self.text_area.insert(tk.END, "! ", "WARNING")
        elif level == "ERROR":
            self.text_area.insert(tk.END, "✘ ", "ERROR")

        self.text_area.insert(tk.END, f"{message}\n", level)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def clear(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)


class StatusLegend(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="상태 설명", padding=10, **kwargs)

        items = [("O", "이름 유사 + 번호 일치"), ("△", "번호만 일치"), ("X", "매칭 없음")]

        self._legend_sym_font = tkfont.Font(
            family="Malgun Gothic", size=9, weight="bold"
        )

        for symbol, desc in items:
            row = ttk.Frame(self)
            row.pack(fill=tk.X, pady=2)

            lbl_sym = ttk.Label(
                row, text=symbol, width=4, anchor="center", font=self._legend_sym_font
            )

            lbl_sym.pack(side=tk.LEFT)

            lbl_desc = ttk.Label(row, text=f":  {desc}")
            lbl_desc.pack(side=tk.LEFT)


class ProgressFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=10, **kwargs)

        self.status_var = tk.StringVar(value="대기 중")
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        self.progress_var = tk.DoubleVar(value=0)
        self.progressbar = ttk.Progressbar(
            self, variable=self.progress_var, mode="determinate"
        )
        self.progressbar.pack(fill=tk.X)

        self._small_font = tkfont.Font(family="Malgun Gothic", size=9)
        self.count_label = ttk.Label(self, text="", anchor="e", font=self._small_font)
        self.count_label.pack(fill=tk.X, pady=(5, 0))

    def update_progress(self, current: int, total: int, filename: str):
        percentage = (current / total) * 100
        self.progress_var.set(percentage)
        self.status_var.set(f"처리 중: {filename}")
        self.count_label.configure(text=f"{int(percentage)}% ({current}/{total})")

    def reset(self):
        self.progress_var.set(0)
        self.status_var.set("대기 중")
        self.count_label.configure(text="")

    def complete(self):
        self.progress_var.set(100)
        self.status_var.set("처리 완료")
        self.count_label.configure(text="100% 완료")
