import customtkinter as ctk
from tkinter import ttk, messagebox
from ..database import listar_livros_bd, remover_livro_bd, buscar_livro_por_id_bd
from ..models import Livro
from .book_dialogs import AdicionarLivroDialog, EditarLivroDialog

class AppMainWindow(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Sistema de Gerenciamento de Biblioteca Pessoal")
        self.geometry("1000x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.actions_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.actions_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.actions_frame.grid_propagate(False)

        self.books_list_frame = ctk.CTkFrame(self)
        self.books_list_frame.grid(row=0, column=1, sticky="nsew", padx=(0,5), pady=5)
        self.books_list_frame.grid_columnconfigure(0, weight=1)
        self.books_list_frame.grid_rowconfigure(1, weight=1)

        self.actions_frame.grid_rowconfigure((0,1,2,3,4,5,6), weight=0)
        self.actions_frame.grid_rowconfigure(7, weight=1)

        self.label_actions = ctk.CTkLabel(self.actions_frame, text="Ações", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_actions.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_add_livro = ctk.CTkButton(self.actions_frame, text="Adicionar Novo Livro", command=self.abrir_dialogo_adicionar_livro)
        self.btn_add_livro.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_edit_livro = ctk.CTkButton(self.actions_frame, text="Editar Livro Selecionado", command=self.abrir_dialogo_editar_livro)
        self.btn_edit_livro.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.btn_edit_livro.configure(state="disabled")

        self.btn_remove_livro = ctk.CTkButton(self.actions_frame, text="Remover Livro Selecionado", command=self.remover_livro_selecionado)
        self.btn_remove_livro.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.btn_remove_livro.configure(state="disabled")
        
        self.btn_gerenciar_autores = ctk.CTkButton(self.actions_frame, text="Gerenciar Autores", command=self.abrir_gerenciador_autores)
        self.btn_gerenciar_autores.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_gerenciar_emprestimos = ctk.CTkButton(self.actions_frame, text="Gerenciar Empréstimos", command=self.abrir_gerenciador_emprestimos)
        self.btn_gerenciar_emprestimos.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.btn_atualizar_lista = ctk.CTkButton(self.actions_frame, text="Atualizar Lista", command=self.carregar_livros)
        self.btn_atualizar_lista.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.label_lista_livros = ctk.CTkLabel(self.books_list_frame, text="Acervo da Biblioteca", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_lista_livros.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        style = ttk.Style(self)
        current_theme = ctk.get_appearance_mode()
        if current_theme == "Dark":
            style.theme_use("default")
            style.configure("Treeview",
                            background="#2b2b2b",
                            foreground="white",
                            fieldbackground="#2b2b2b",
                            borderwidth=0, rowheight=25)
            style.map('Treeview', background=[('selected', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
            style.configure("Treeview.Heading",
                            background="#202020",
                            foreground="white",
                            relief="flat",
                            font=('Calibri', 10, 'bold'))
            style.map("Treeview.Heading",
                      background=[('active', '#303030')])
        else:
            style.theme_use("default")
            style.configure("Treeview",
                            background="white",
                            foreground="black",
                            fieldbackground="white",
                            borderwidth=0, rowheight=25)
            style.map('Treeview', background=[('selected', ctk.ThemeManager.theme["CTkButton"]["fg_color"][0])])
            style.configure("Treeview.Heading",
                            background="#ebebeb",
                            foreground="black",
                            relief="flat",
                            font=('Calibri', 10, 'bold'))
            style.map("Treeview.Heading",
                      background=[('active', '#d5d5d5')])


        self.tree_livros = ttk.Treeview(
            self.books_list_frame,
            columns=("ID", "Título", "Autor(es)", "ISBN", "Ano"),
            show="headings"
        )
        self.tree_livros.heading("ID", text="ID")
        self.tree_livros.heading("Título", text="Título")
        self.tree_livros.heading("Autor(es)", text="Autor(es)")
        self.tree_livros.heading("ISBN", text="ISBN")
        self.tree_livros.heading("Ano", text="Ano Public.")

        self.tree_livros.column("ID", width=200, minwidth=150, stretch=False, anchor="w")
        self.tree_livros.column("Título", width=300, minwidth=150, stretch=True, anchor="w")
        self.tree_livros.column("Autor(es)", width=250, minwidth=150, stretch=True, anchor="w")
        self.tree_livros.column("ISBN", width=150, minwidth=100, stretch=False, anchor="w")
        self.tree_livros.column("Ano", width=80, minwidth=60, stretch=False, anchor="center")

        self.tree_livros.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.scrollbar_livros_y = ctk.CTkScrollbar(self.books_list_frame, command=self.tree_livros.yview)
        self.scrollbar_livros_y.grid(row=1, column=1, sticky="ns", pady=10, padx=(0,20))
        self.tree_livros.configure(yscrollcommand=self.scrollbar_livros_y.set)

        self.tree_livros.bind("<<TreeviewSelect>>", self.ao_selecionar_livro)
        self.tree_livros.bind("<Double-1>", self.ao_duplo_clique_livro)


        self.carregar_livros()

    def carregar_livros(self):
        for item in self.tree_livros.get_children():
            self.tree_livros.delete(item)

        livros: list[Livro] = listar_livros_bd()
        if livros:
            for livro in livros:
                nomes_autores = ", ".join([autor.nome for autor in livro.autores]) if livro.autores else "N/A"
                self.tree_livros.insert("", "end", iid=livro.id_item, values=(
                    livro.id_item,
                    livro.titulo,
                    nomes_autores,
                    livro.isbn,
                    livro.ano_publicacao if livro.ano_publicacao else "N/A"
                ))
        self.desabilitar_botoes_edicao_remocao()


    def ao_selecionar_livro(self, event=None):
        selecionados = self.tree_livros.selection()
        if selecionados:
            self.btn_edit_livro.configure(state="normal")
            self.btn_remove_livro.configure(state="normal")
        else:
            self.desabilitar_botoes_edicao_remocao()

    def ao_duplo_clique_livro(self, event=None):
        """Chamado com duplo clique em um livro para editar."""
        if self.obter_id_livro_selecionado():
            self.abrir_dialogo_editar_livro()


    def desabilitar_botoes_edicao_remocao(self):
        self.btn_edit_livro.configure(state="disabled")
        self.btn_remove_livro.configure(state="disabled")
        
    def obter_id_livro_selecionado(self) -> str | None:
        selecionados = self.tree_livros.selection()
        if selecionados:
            return selecionados[0] 
        return None

    def abrir_dialogo_adicionar_livro(self):
        print("Ação: Abrir diálogo para adicionar novo livro.")
        dialog = AdicionarLivroDialog(master=self)
        self.wait_window(dialog)
        self.carregar_livros()

    def abrir_dialogo_editar_livro(self):
        id_livro_sel = self.obter_id_livro_selecionado()
        if id_livro_sel:
            print(f"Ação: Abrir diálogo para editar livro ID: {id_livro_sel}")
            dialog = EditarLivroDialog(master=self, id_livro_para_editar=id_livro_sel)
            self.wait_window(dialog)
            self.carregar_livros()
        else:
            messagebox.showwarning("Nenhum Livro Selecionado", "Por favor, selecione um livro na lista para editar.", parent=self)


    def remover_livro_selecionado(self):
        id_livro_sel = self.obter_id_livro_selecionado()
        if id_livro_sel:
            livro_obj = buscar_livro_por_id_bd(id_livro_sel)
            nome_livro = livro_obj.titulo if livro_obj else f"ID {id_livro_sel}"

            confirmar = messagebox.askyesno(
                title="Confirmar Remoção",
                message=f"Tem certeza que deseja remover o livro '{nome_livro}'?\nEsta ação não pode ser desfeita.",
                icon=messagebox.WARNING,
                parent=self
            )
            if confirmar:
                if remover_livro_bd(id_livro_sel):
                    messagebox.showinfo("Sucesso", f"Livro '{nome_livro}' removido com sucesso!", parent=self)
                    self.carregar_livros()
                else:
                    messagebox.showerror("Erro no Banco de Dados", f"Falha ao remover o livro '{nome_livro}'.", parent=self)
        else:
            messagebox.showwarning("Nenhum Livro Selecionado", "Por favor, selecione um livro na lista para remover.", parent=self)

    def abrir_gerenciador_autores(self):
        messagebox.showinfo("Em Desenvolvimento", "A funcionalidade de Gerenciar Autores ainda não foi implementada.", parent=self)
        pass

    def abrir_gerenciador_emprestimos(self):
        messagebox.showinfo("Em Desenvolvimento", "A funcionalidade de Gerenciar Empréstimos ainda não foi implementada.", parent=self)
        pass

if __name__ == "__main__":
    import sys
    import os
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT, PACKAGE_PARENT)))

    from package.database import inicializar_bd
    inicializar_bd()

    app = AppMainWindow()
    app.mainloop()