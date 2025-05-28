import uuid
from datetime import date

class Autor:
    def __init__(self, nome: str, data_nascimento: date = None, biografia: str = "", id_autor: str = None):
        self._id_autor = id_autor if id_autor else str(uuid.uuid4())
        self._nome = nome
        self._data_nascimento = data_nascimento
        self._biografia = biografia

    @property
    def id_autor(self) -> str:
        return self._id_autor

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, nome: str):
        if not nome or not isinstance(nome, str):
            raise ValueError("Nome do autor não pode ser vazio e deve ser uma string.")
        self._nome = nome

    @property
    def data_nascimento(self) -> date:
        return self._data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, data_nascimento: date):
        if data_nascimento and not isinstance(data_nascimento, date):
            raise ValueError("Data de nascimento deve ser um objeto date.")
        self._data_nascimento = data_nascimento
        
    @property
    def biografia(self) -> str:
        return self._biografia

    @biografia.setter
    def biografia(self, biografia: str):
        self._biografia = biografia

    def __str__(self) -> str:
        return f"Autor(ID: {self._id_autor}, Nome: {self._nome})"

    def __repr__(self) -> str:
        return f"Autor(nome='{self._nome}', id_autor='{self._id_autor}')"

class ItemBiblioteca:
    def __init__(self, titulo: str, ano_publicacao: int = None, id_item: str = None):
        self._id_item = id_item if id_item else str(uuid.uuid4())
        self._titulo = titulo
        self._ano_publicacao = ano_publicacao

    @property
    def id_item(self) -> str:
        return self._id_item

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, titulo: str):
        if not titulo or not isinstance(titulo, str):
            raise ValueError("Título não pode ser vazio e deve ser uma string.")
        self._titulo = titulo

    @property
    def ano_publicacao(self) -> int:
        return self._ano_publicacao

    @ano_publicacao.setter
    def ano_publicacao(self, ano: int):
        if ano and (not isinstance(ano, int) or ano > date.today().year):
            raise ValueError(f"Ano de publicação deve ser um número inteiro válido e não futuro (até {date.today().year}).")
        self._ano_publicacao = ano

    def obter_descricao_curta(self) -> str: 
        return f"ID: {self._id_item}, Título: {self._titulo}"

    def __str__(self) -> str:
        return self.obter_descricao_curta()


class Livro(ItemBiblioteca):
    def __init__(self, titulo: str, isbn: str = "", editora: str = "", numero_paginas: int = 0,
                 sinopse: str = "", ano_publicacao: int = None, id_livro: str = None,
                 autores: list[Autor] = None):
        super().__init__(titulo, ano_publicacao, id_item=id_livro)
        self._isbn = isbn
        self._editora = editora
        self._numero_paginas = numero_paginas
        self._sinopse = sinopse
        self._autores = autores if autores else []

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, isbn: str):
        self._isbn = isbn

    @property
    def editora(self) -> str:
        return self._editora
    
    @editora.setter
    def editora(self, editora: str):
        self._editora = editora

    @property
    def numero_paginas(self) -> int:
        return self._numero_paginas

    @numero_paginas.setter
    def numero_paginas(self, num_paginas: int):
        if not isinstance(num_paginas, int) or num_paginas < 0:
            raise ValueError("Número de páginas deve ser um inteiro não negativo.")
        self._numero_paginas = num_paginas
        
    @property
    def sinopse(self) -> str:
        return self._sinopse

    @sinopse.setter
    def sinopse(self, sinopse: str):
        self._sinopse = sinopse

    @property
    def autores(self) -> list[Autor]:
        return self._autores

    def adicionar_autor(self, autor: Autor):
        if not isinstance(autor, Autor):
            raise TypeError("Só é possível adicionar objetos do tipo Autor.")
        if autor not in self._autores:
            self._autores.append(autor)

    def remover_autor(self, autor: Autor):
        if autor in self._autores:
            self._autores.remove(autor)

    def obter_descricao_curta(self) -> str:
        nomes_autores = ", ".join([autor.nome for autor in self._autores]) if self._autores else "Desconhecido"
        return f"Livro: {self.titulo} por {nomes_autores} (Ano: {self.ano_publicacao if self.ano_publicacao else 'N/A'})"

    def __repr__(self) -> str:
        return f"Livro(titulo='{self.titulo}', isbn='{self.isbn}', id_item='{self.id_item}')"

class Emprestimo:
    def __init__(self, livro: Livro, nome_usuario: str, data_emprestimo: date, data_devolucao_prevista: date, id_emprestimo: str = None):
        if not isinstance(livro, Livro):
            raise TypeError("Empréstimo deve ser de um objeto Livro.")
        if not nome_usuario or not isinstance(nome_usuario, str):
            raise ValueError("Nome do usuário não pode ser vazio.")

        self._id_emprestimo = id_emprestimo if id_emprestimo else str(uuid.uuid4())
        self._livro = livro
        self._nome_usuario = nome_usuario
        self._data_emprestimo = data_emprestimo
        self._data_devolucao_prevista = data_devolucao_prevista
        self._data_devolucao_efetiva = None

    @property
    def id_emprestimo(self) -> str:
        return self._id_emprestimo

    @property
    def livro(self) -> Livro:
        return self._livro

    @property
    def nome_usuario(self) -> str:
        return self._nome_usuario
    
    @property
    def data_emprestimo(self) -> date:
        return self._data_emprestimo

    @property
    def data_devolucao_prevista(self) -> date:
        return self._data_devolucao_prevista
        
    @property
    def data_devolucao_efetiva(self) -> date:
        return self._data_devolucao_efetiva

    def registrar_devolucao(self, data_devolucao: date):
        if data_devolucao < self._data_emprestimo:
            raise ValueError("Data de devolução não pode ser anterior à data de empréstimo.")
        self._data_devolucao_efetiva = data_devolucao
        print(f"Livro '{self.livro.titulo}' devolvido por {self.nome_usuario} em {data_devolucao}.")

    def __str__(self) -> str:
        status = "Devolvido" if self._data_devolucao_efetiva else "Emprestado"
        return (f"Empréstimo ID: {self.id_emprestimo}\n"
                f"  Livro: {self.livro.titulo}\n"
                f"  Usuário: {self.nome_usuario}\n"
                f"  Data Empréstimo: {self.data_emprestimo}\n"
                f"  Devolução Prevista: {self.data_devolucao_prevista}\n"
                f"  Status: {status}" +
                (f"\n  Devolvido em: {self.data_devolucao_efetiva}" if self.data_devolucao_efetiva else ""))
