import sv_ttk
import darkdetect
import tkinter as tk
from tkinter import font


def get_system_theme() -> str:
    theme = darkdetect.theme()
    if theme:
        return theme.lower()
    return "dark"


def apply_theme(theme: str) -> None:
    sv_ttk.set_theme(theme)


def init_theme(root: tk.Tk) -> None:
    # 맑은 고딕 기본 폰트 설정
    family = "Malgun Gothic"

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=family, size=10)

    text_font = font.nametofont("TkTextFont")
    text_font.configure(family=family, size=10)

    theme = get_system_theme()
    apply_theme(theme)
