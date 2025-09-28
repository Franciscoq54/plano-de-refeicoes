"""
Frame para exibir as listas de compras guardadas.
Permite visualizar todas as listas anteriores
"""
import tkinter as tk
from utils.lista_compras import obterListasComprasGuardadas
from visual.cores import BACKGROUND

#Frame Tkinter para exibicao das listas de compras guardadas
class ListasComprasFrame(tk.Frame):
    #Inicializa o frame das listas de compras
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.master = master
        self.create_widgets()
    #Cria e organiza todos os widgets do frame, apresentando as listas guardadas
    def create_widgets(self):
        tk.Label(self, text="Listas de Compras Anteriores", font=("Helvetica", 16), bg=BACKGROUND).pack(pady=10)

        listas = obterListasComprasGuardadas()

        if not listas:
            tk.Label(self, text="Nenhuma lista encontrada.", bg=BACKGROUND).pack(pady=10)
        else:
            canvas_frame = tk.Frame(self, bg=BACKGROUND)
            canvas_frame.pack(fill="both", expand=True)

            #usa canvas e scrollbar para suportar muitas listas
            canvas = tk.Canvas(canvas_frame, height=400, bg=BACKGROUND)
            scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=BACKGROUND)

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for identificador in sorted(listas.keys(), reverse=True):
                ingredientes = listas[identificador]
                frame = tk.Frame(scrollable_frame, relief=tk.RIDGE, borderwidth=2, padx=10, pady=5, bg=BACKGROUND)
                frame.pack(padx=10, pady=5, fill="x")

                tk.Label(frame, text=f"Data: {identificador}", font=("Helvetica", 12, "bold"), bg=BACKGROUND).pack(anchor="w")

                for nome, info in ingredientes.items():
                    if isinstance(info, dict):
                        quantidade = info.get('quantidade', 0)
                        unidade = info.get('unidade', '')
                    else:
                        quantidade= info
                        unidade  = ''
                    linha = f" - {nome}: {round(quantidade, 2)} {unidade}"
                    tk.Label(frame, text=linha, bg=BACKGROUND).pack(anchor="w")
        tk.Button(self, text="Voltar", command=self.voltar).pack(pady=20)

    #volta ao menu inicial da aplicacao
    def voltar(self):
        from interface.menu_inicial import MenuInicial
        for widget in self.master.winfo_children():
            widget.destroy()
        MenuInicial(self.master).pack(fill="both", expand=True)

#Frame para visualizacao detalhada de uma lista de ingredientes
class ListaComprasVisualizacaoFrame(tk.Frame):
    #Inicializa o frame de visualizações de uma lista de compras
    def __init__(self, master, lista_ingredientes, callback_voltar):
        super().__init__(master, bg=BACKGROUND)
        self.lista_ingredientes = lista_ingredientes
        self.callback_voltar = callback_voltar
        self.create_widgets()
        
    #constroi os widgets para exibir a lista de compras
    def create_widgets(self):
        tk.Label(self, text="Lista de Compras", font=("Helvetica", 16), bg=BACKGROUND).pack(pady=10)
        lista_text = tk.Text(self, height=20, width=80)
        lista_text.pack(padx=10, pady=10)
        if self.lista_ingredientes:
            for nome, info in self.lista_ingredientes.items():
                if isinstance(info, dict):
                    quantidade = info.get('quantidade', 0)
                    unidade = info.get('unidade', '')
                else:
                    quantidade = info
                    unidade = ''
                lista_text.insert(tk.END, f" - {nome}: {round(info['quantidade'], 2)} {info.get('unidade', '')}\n")
        else:
            lista_text.insert(tk.END, "Nenhum ingrediente encontrado.")
        tk.Button(self, text="Voltar", command=self.callback_voltar).pack(pady=10)