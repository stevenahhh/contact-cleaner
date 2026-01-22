import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import List, Callable, Optional
from datetime import datetime

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


class FileListFrame(ttk.LabelFrame):
    def __init__(
        self, parent, title="선택된 파일", on_add: Optional[Callable] = None, **kwargs
    ):
        self.title_base = title
        super().__init__(parent, text=f"{self.title_base} (0개)", padding=15, **kwargs)
        self.files: List[str] = []
        self._listbox_font = tkfont.Font(family="Malgun Gothic", size=11)
        self._setup_ui(on_add)

    def _setup_ui(self, on_add):
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create container for listbox and drag hint overlay
        container = tk.Frame(list_frame, bd=0, highlightthickness=0)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            container,
            selectmode=tk.EXTENDED,
            height=12,
            bd=0,
            highlightthickness=1,
            relief="flat",
            font=self._listbox_font,
            exportselection=False,
        )
        self.listbox.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.listbox.bind('<Configure>', lambda e: None)
        
        if HAS_DND:
            self._hint_font = tkfont.Font(family="Malgun Gothic", size=12)
            list_bg = self.listbox.cget("bg")
            self.hint_label = tk.Label(
                container,
                text="파일을 여기에 드래그하세요\n또는 '파일 추가' 버튼 클릭",
                font=self._hint_font,
                fg="#999999",
                bg=list_bg,
                justify=tk.CENTER
            )
            self.hint_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            # Show hint immediately since list is empty on init
            self.hint_label.lift()
        
        self._setup_drag_drop()

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
    
    def _setup_drag_drop(self):
        if not HAS_DND:
            return
        
        try:
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind('<<Drop>>', self._on_drop)
            self.listbox.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.listbox.dnd_bind('<<DragLeave>>', self._on_drag_leave)
        except Exception:
            pass
    
    def _on_drag_enter(self, event):
        # Highlight on drag enter
        if hasattr(self, 'hint_label'):
            self.hint_label.config(fg="#2196F3")
    
    def _on_drag_leave(self, event):
        # Remove highlight on drag leave
        if hasattr(self, 'hint_label'):
            self.hint_label.config(fg="#999999")
    
    def _on_drop(self, event):
        files = self.listbox.tk.splitlist(event.data)
        valid_files = [f for f in files if f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        if valid_files:
            self.add_files(valid_files)
        self._update_hint_visibility()

    def add_files(self, new_files):
        for f in new_files:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, f)
        self._update_label()
        self._update_hint_visibility()

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
        self._update_hint_visibility()
    
    def _update_hint_visibility(self):
        # Show hint only when listbox is empty and DND is available
        if not HAS_DND or not hasattr(self, 'hint_label'):
            return
        
        if len(self.files) == 0:
            self.hint_label.lift()  # Show hint on top
        else:
            self.hint_label.lower()  # Hide hint behind listbox


class LogFrame(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="로그 메시지", padding=15, **kwargs)
        self._log_font = tkfont.Font(family="Malgun Gothic", size=11)
        self._link_font = tkfont.Font(family="Malgun Gothic", size=11, underline=True)
        self._setup_ui()

    def _setup_ui(self):
        self.text_area = tk.Text(
            self,
            height=2,
            font=self._log_font,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bd=0,
            highlightthickness=1,
            cursor="arrow",
            exportselection=False,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.bind('<Configure>', lambda e: None)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        self.text_area.tag_configure("INFO", foreground="#2196F3")
        self.text_area.tag_configure("SUCCESS", foreground="#4CAF50")
        self.text_area.tag_configure("WARNING", foreground="#FF9800")
        self.text_area.tag_configure("ERROR", foreground="#F44336")
        self.text_area.tag_configure("TIME", foreground="#888888")
        self.text_area.tag_configure("LINK", foreground="#1976D2", font=self._link_font)

        self.text_area.tag_bind("LINK", "<Button-1>", self._on_link_click)
        self.text_area.tag_bind("LINK", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("LINK", "<Leave>", lambda e: self.text_area.config(cursor="arrow"))

    def log(self, message: str, level: str = "INFO", link: str = ""):
        self.text_area.config(state=tk.NORMAL)

        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.text_area.insert(tk.END, timestamp, "TIME")

        if level == "SUCCESS":
            self.text_area.insert(tk.END, "✓ ", "SUCCESS")
        elif level == "WARNING":
            self.text_area.insert(tk.END, "! ", "WARNING")
        elif level == "ERROR":
            self.text_area.insert(tk.END, "✘ ", "ERROR")

        self.text_area.insert(tk.END, f"{message}", level)

        if link:
            self.text_area.insert(tk.END, "\n  → ", level)
            link_tag = f"link_{id(link)}"
            self.text_area.tag_configure(link_tag, foreground="#1976D2", font=self._link_font)
            self.text_area.tag_bind(link_tag, "<Button-1>", lambda e, p=link: self._open_folder(p))
            self.text_area.tag_bind(link_tag, "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
            self.text_area.tag_bind(link_tag, "<Leave>", lambda e: self.text_area.config(cursor="arrow"))
            self.text_area.insert(tk.END, link, link_tag)

        self.text_area.insert(tk.END, "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def _on_link_click(self, event):
        pass

    def _open_folder(self, path: str):
        from pathlib import Path
        import subprocess
        import os
        import sys
        
        file_path = Path(path)
        if file_path.exists():
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(file_path)])
            else:
                subprocess.run(["xdg-open", str(file_path)])

    def clear(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)


class StatusLegend(ttk.LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="상태 설명", padding=8, **kwargs)

        items = [
            ("O", "이름+번호 일치"),
            ("△(번호)", "번호만 일치"),
            ("△(이름)", "이름만 일치"),
            ("X", "매칭 없음")
        ]

        self._legend_sym_font = tkfont.Font(
            family="Malgun Gothic", size=10, weight="bold"
        )
        self._legend_desc_font = tkfont.Font(
            family="Malgun Gothic", size=10
        )

        # Horizontal layout
        for i, (symbol, desc) in enumerate(items):
            lbl_sym = ttk.Label(
                self, text=symbol, font=self._legend_sym_font
            )
            lbl_sym.pack(side=tk.LEFT, padx=(0, 2))

            lbl_desc = ttk.Label(self, text=f": {desc}", font=self._legend_desc_font)
            lbl_desc.pack(side=tk.LEFT, padx=(0, 15) if i < len(items) - 1 else (0, 0))


class ProgressFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, padding=10, **kwargs)

        self.status_var = tk.StringVar(value="대기 중")
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progressbar.pack(fill=tk.X)

    def update_progress(self, current: int, total: int, status: str = "처리 중"):
        if total > 0:
            percent = int((current / total) * 100)
            self.progressbar["value"] = percent
            self.status_var.set(f"{status}: {current:,}/{total:,} ({percent}%)")
        else:
            self.progressbar["value"] = 0
            self.status_var.set(status)

    def reset(self):
        self.progressbar["value"] = 0
        self.status_var.set("대기 중")

    def complete(self):
        self.progressbar["value"] = 100
        self.status_var.set("처리 완료")
