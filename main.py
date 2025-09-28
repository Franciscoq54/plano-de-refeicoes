"""
Ponto de entrada da aplição Planeador de Refeições
Inicializa a interface grafica Tkinter e apresenta o menu principal ao utilizador
"""

import tkinter as tk
from interface.menu_inicial import MenuInicial

def main():
    root = tk.Tk()
    root.title("Planeador de Refeições")
    root.geometry("800x600")
    MenuInicial(root).pack(fill = "both", expand= True)
    root.mainloop()

if __name__ == "__main__":
    main()