"""
Contem funções para aplicar estilos globais aos widgets Tkinter da aplicação´
Permite uniformizar o aspeto dos botoes, labels e entradas de texto.
"""

from tkinter import ttk
from .cores import PRIMARY, SECONDARY, BUTTON_TEXT

def aplicar_estilos():
    style = ttk.Style()
    #usa um tema base
    style.theme_use("clam")
    #botoes
    style.configure("TButton", background=PRIMARY, foreground=BUTTON_TEXT, font=("Helvetica", 11, "bold"), borderwidth=1)
    style.map("TButton", background=[("active", SECONDARY)], foreground=[("active", BUTTON_TEXT)])
    #combobox
    style.configure("TCombobox", fieldbackground="#fff", background=PRIMARY)
    