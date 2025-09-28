"""
Frame que apresenta o historico de planos de refeicoes, permitindo visualizar
rapidamente planos guardados anteriormente
"""
import tkinter as tk
from utils.historico import mostrarHistorico
from visual.cores import BACKGROUND

#Frame Tkinter para exibicao do historico dos planos
class HistoricoFrame(tk.Frame):
    #inicializa o frame do historico
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.create_widgets()
    #cria e organiza todos os widgets do frame, construindo a lista do historico
    def create_widgets(self):
        tk.Label(self, text="Histórico de Planos de Refeições", font=("Helvetica", 16), bg=BACKGROUND).pack(pady=10)

        container = tk.Frame(self, bg=BACKGROUND)
        container.pack(fill="both", expand=True)

        #Frame com scroll para suportar muitos planos
        canvas = tk.Canvas(container, borderwidth=0, height=400, bg=BACKGROUND)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BACKGROUND)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        historico = mostrarHistorico()
        if not historico:
            tk.Label(scroll_frame, text="Nenhum plano de refeições foi guardado ainda.", bg=BACKGROUND).pack(pady=10)
        else:
            for plano in historico:
                frame_plano = tk.LabelFrame(scroll_frame, text=f"Plano de {plano['data']}", font=("Helvetica", 12, "bold"), padx=10, pady=5, bg=BACKGROUND) 
                frame_plano.pack(fill="x", padx=10, pady=5)
                tk.Label(frame_plano, text=f"Dieta: {plano['dieta']}", bg=BACKGROUND).pack(anchor="w")
                tk.Label(frame_plano, text=f"Calorias: {plano['calorias']}", bg=BACKGROUND).pack(anchor="w")
                tk.Label(frame_plano, text="Refeições:", bg=BACKGROUND).pack(anchor="w")

                for refeicao in plano.get("refeicoes", []):
                    if isinstance(refeicao, dict):
                        tk.Label(frame_plano, text=f" - {refeicao.get('title', '')}", bg=BACKGROUND).pack(anchor="w")
                    else:
                        tk.Label(frame_plano, text=f" - {refeicao}", bg=BACKGROUND).pack(anchor="w")
        tk.Button(self, text="Voltar", command=self.voltar).pack(pady=10)
    
    #Volta ao menu inicial da aplicacao
    def voltar(self):
        from interface.menu_inicial import MenuInicial
        self._trocar_frame(MenuInicial)
    #troca o frame atual pelo frame dado
    def _trocar_frame(self, FrameClass):
        for widget in self.master.winfo_children():
            widget.destroy()
        FrameClass(self.master).pack(fill="both", expand=True)
