import customtkinter as ctk
from tkinter import messagebox
from datetime import date

from ..models import Livro, Autor
from ..database import (
    adicionar_livro_bd,
    buscar_livro_por_id_bd,
    atualizar_livro_bd,
    listar_autores_bd, 
    adicionar_autor_bd, 
    buscar_autor_por_id_bd 
)

class BaseLivroDialog(ctk.CTkToplevel):
    """Classe base para diálogos de adicionar e editar livro."""
    def __init__(self, master, title="Diálogo de Livro"):
        super().__init__(master)
        self.title(title)
        self.geometry("550x650") 
        self.resizable(False, False)
        self.transient(master) 
        self.grab_set() 

        self.livro_result = None 

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.main_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = ctk.CTkEntry(self.main_frame, width=350)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.main_frame, text="Autor(es) (sep. por vírgula):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_autores = ctk.CTkEntry(self.main_frame)
        self.entry_autores.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(self.main_frame, text="Ex: J.R.R. Tolkien, George R.R. Martin", font=("Arial", 9)).grid(row=2, column=1, padx=5, sticky="w")

        ctk.CTkLabel(self.main_frame, text="ISBN:").grid(row=3, column=0, padx=5, pady=(10,5), sticky="w")
        self.entry_isbn = ctk.CTkEntry(self.main_frame)
        self.entry_isbn.grid(row=3, column=1, padx=5, pady=(10,5), sticky="ew")

        ctk.CTkLabel(self.main_frame, text="Ano de Publicação:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_ano = ctk.CTkEntry(self.main_frame)
        self.entry_ano.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.main_frame, text="Editora:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.entry_editora = ctk.CTkEntry(self.main_frame)
        self.entry_editora.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.main_frame, text="Nº de Páginas:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.entry_paginas = ctk.CTkEntry(self.main_frame)
        self.entry_paginas.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.main_frame, text="Sinopse:").grid(row=7, column=0, padx=5, pady=5, sticky="nw")
        self.textbox_sinopse = ctk.CTkTextbox(self.main_frame, height=120, wrap="word")
        self.textbox_sinopse.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=8, column=0, columnspan=2, pady=(20,0))

        self.btn_salvar = ctk.CTkButton(self.button_frame, text="Salvar", command=self.salvar_livro)
        self.btn_salvar.pack(side="left", padx=10)

        self.btn_cancelar = ctk.CTkButton(self.button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.btn_cancelar.pack(side="left", padx=10)

    def _processar_autores_str(self, autores_str: str) -> list[Autor]:
        nomes_autores = [nome.strip() for nome in autores_str.split(',') if nome.strip()]
        autores_obj_list = []
        
        autores_existentes_bd = listar_autores_bd()
        mapa_nomes_autores_bd = {autor.nome.lower(): autor for autor in autores_existentes_bd}

        for nome_autor_str in nomes_autores:
            autor_encontrado = mapa_nomes_autores_bd.get(nome_autor_str.lower())
            if autor_encontrado:
                autores_obj_list.append(autor_encontrado)
            else:
                novo_autor = Autor(nome=nome_autor_str)
                if adicionar_autor_bd(novo_autor): 
                    autores_obj_list.append(novo_autor)
                else:
                    print(f"AVISO: Não foi possível adicionar o novo autor '{nome_autor_str}' ao banco de dados.")
        return autores_obj_list

    def salvar_livro(self):
        raise NotImplementedError("O método 'salvar_livro' deve ser implementado pela subclasse.")


class AdicionarLivroDialog(BaseLivroDialog):
    def __init__(self, master):
        super().__init__(master, title="Adicionar Novo Livro")

    def salvar_livro(self):
        titulo = self.entry_titulo.get().strip()
        autores_str = self.entry_autores.get().strip()
        isbn = self.entry_isbn.get().strip()
        ano_str = self.entry_ano.get().strip()
        editora = self.entry_editora.get().strip()
        paginas_str = self.entry_paginas.get().strip()
        sinopse = self.textbox_sinopse.get("1.0", "end-1c").strip()

        if not titulo:
            messagebox.showerror("Erro de Validação", "O campo 'Título' é obrigatório.", parent=self)
            return
        if not autores_str:
            messagebox.showerror("Erro de Validação", "O campo 'Autor(es)' é obrigatório.", parent=self)
            return

        ano = None
        if ano_str:
            try:
                ano = int(ano_str)
                if ano > date.today().year or ano < 0: 
                    messagebox.showerror("Erro de Validação", f"Ano de publicação inválido. Deve ser entre 0 e {date.today().year}.", parent=self)
                    return
            except ValueError:
                messagebox.showerror("Erro de Validação", "Ano de publicação deve ser um número.", parent=self)
                return
        
        paginas = 0
        if paginas_str:
            try:
                paginas = int(paginas_str)
                if paginas < 0:
                     messagebox.showerror("Erro de Validação", "Número de páginas não pode ser negativo.", parent=self)
                     return
            except ValueError:
                messagebox.showerror("Erro de Validação", "Número de páginas deve ser um número.", parent=self)
                return

        autores_obj_list = self._processar_autores_str(autores_str)
        if not autores_obj_list and autores_str: 
            messagebox.showwarning("Aviso Autores", "Não foi possível processar os autores. Verifique os nomes ou tente novamente.", parent=self)
        
        novo_livro = Livro(
            titulo=titulo,
            autores=autores_obj_list,
            isbn=isbn,
            ano_publicacao=ano,
            editora=editora,
            numero_paginas=paginas,
            sinopse=sinopse
        )

        if adicionar_livro_bd(novo_livro):
            messagebox.showinfo("Sucesso", f"Livro '{novo_livro.titulo}' adicionado com sucesso!", parent=self.master) 
            self.livro_result = novo_livro 
            self.destroy() 
        else:
            messagebox.showerror("Erro no Banco de Dados", "Não foi possível adicionar o livro ao banco de dados.", parent=self)


class EditarLivroDialog(BaseLivroDialog):
    def __init__(self, master, id_livro_para_editar: str):
        super().__init__(master, title="Editar Livro")
        self.id_livro = id_livro_para_editar
        self.livro_original: Livro | None = None
        self._carregar_dados_livro()

    def _carregar_dados_livro(self):
        self.livro_original = buscar_livro_por_id_bd(self.id_livro)
        if not self.livro_original:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do livro para edição.", parent=self)
            self.destroy()
            return

        self.entry_titulo.insert(0, self.livro_original.titulo)
        
        autores_nomes_str = ", ".join([autor.nome for autor in self.livro_original.autores])
        self.entry_autores.insert(0, autores_nomes_str)
        
        self.entry_isbn.insert(0, self.livro_original.isbn if self.livro_original.isbn else "")
        self.entry_ano.insert(0, str(self.livro_original.ano_publicacao) if self.livro_original.ano_publicacao is not None else "")
        self.entry_editora.insert(0, self.livro_original.editora if self.livro_original.editora else "")
        self.entry_paginas.insert(0, str(self.livro_original.numero_paginas) if self.livro_original.numero_paginas is not None else "")
        self.textbox_sinopse.insert("1.0", self.livro_original.sinopse if self.livro_original.sinopse else "")

    def salvar_livro(self):
        if not self.livro_original:
            return

        titulo = self.entry_titulo.get().strip()
        autores_str = self.entry_autores.get().strip()
        isbn = self.entry_isbn.get().strip()
        ano_str = self.entry_ano.get().strip()
        editora = self.entry_editora.get().strip()
        paginas_str = self.entry_paginas.get().strip()
        sinopse = self.textbox_sinopse.get("1.0", "end-1c").strip()

        if not titulo:
            messagebox.showerror("Erro de Validação", "O campo 'Título' é obrigatório.", parent=self)
            return
        if not autores_str:
            messagebox.showerror("Erro de Validação", "O campo 'Autor(es)' é obrigatório.", parent=self)
            return

        ano = None
        if ano_str:
            try:
                ano = int(ano_str)
                if ano > date.today().year or ano < 0:
                    messagebox.showerror("Erro de Validação", f"Ano de publicação inválido. Deve ser entre 0 e {date.today().year}.", parent=self)
                    return
            except ValueError:
                messagebox.showerror("Erro de Validação", "Ano de publicação deve ser um número.", parent=self)
                return
        
        paginas = 0
        if paginas_str:
            try:
                paginas = int(paginas_str)
                if paginas < 0:
                     messagebox.showerror("Erro de Validação", "Número de páginas não pode ser negativo.", parent=self)
                     return
            except ValueError:
                messagebox.showerror("Erro de Validação", "Número de páginas deve ser um número.", parent=self)
                return

        autores_obj_list = self._processar_autores_str(autores_str)
        if not autores_obj_list and autores_str:
            messagebox.showwarning("Aviso Autores", "Não foi possível processar os autores. Verifique os nomes ou tente novamente.", parent=self)

        self.livro_original.titulo = titulo
        
        self.livro_original._autores.clear()
        for autor_obj in autores_obj_list:
            self.livro_original.adicionar_autor(autor_obj)
            
        self.livro_original.isbn = isbn
        self.livro_original.ano_publicacao = ano
        self.livro_original.editora = editora
        self.livro_original.numero_paginas = paginas
        self.livro_original.sinopse = sinopse
        
        if atualizar_livro_bd(self.livro_original):
            messagebox.showinfo("Sucesso", f"Livro '{self.livro_original.titulo}' atualizado com sucesso!", parent=self.master)
            self.livro_result = self.livro_original 
            self.destroy()
        else:
            messagebox.showerror("Erro no Banco de Dados", "Não foi possível atualizar o livro no banco de dados.", parent=self)