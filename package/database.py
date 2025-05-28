import sqlite3
import os
from datetime import date, datetime
from .models import Autor, Livro, Emprestimo

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DATABASE_NAME = 'biblioteca.db'
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

os.makedirs(DATABASE_DIR, exist_ok=True)

def conectar_bd():
    """Conecta ao banco de Dados SQLite e retorna a conexão e o cursor."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

def fechar_bd(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.commit()
        conn.close()

def inicializar_bd():
    """Cria as tabelas no banco de dados se elas não existirem."""
    conn, cursor = conectar_bd()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autores (
                id_autor TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                data_nascimento TEXT, -- Armazenar como YYYY-MM-DD
                biografia TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livros (
                id_livro TEXT PRIMARY KEY, -- id_item da classe base ItemBiblioteca
                titulo TEXT NOT NULL,
                ano_publicacao INTEGER,
                isbn TEXT UNIQUE, -- ISBN deve ser único
                editora TEXT,
                numero_paginas INTEGER,
                sinopse TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livros_autores (
                livro_id TEXT NOT NULL,
                autor_id TEXT NOT NULL,
                FOREIGN KEY (livro_id) REFERENCES livros (id_livro) ON DELETE CASCADE,
                FOREIGN KEY (autor_id) REFERENCES autores (id_autor) ON DELETE CASCADE,
                PRIMARY KEY (livro_id, autor_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emprestimos (
                id_emprestimo TEXT PRIMARY KEY,
                livro_id TEXT NOT NULL,
                nome_usuario TEXT NOT NULL,
                data_emprestimo TEXT NOT NULL, -- Armazenar como YYYY-MM-DD
                data_devolucao_prevista TEXT NOT NULL, -- Armazenar como YYYY-MM-DD
                data_devolucao_efetiva TEXT, -- Armazenar como YYYY-MM-DD
                FOREIGN KEY (livro_id) REFERENCES livros (id_livro) ON DELETE CASCADE
            )
        ''')
        print("Banco de dados inicializado e tabelas criadas (se não existiam).")
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        fechar_bd(conn)

def adicionar_autor_bd(autor: Autor):
    conn, cursor = conectar_bd()
    try:
        data_nasc_str = autor.data_nascimento.isoformat() if autor.data_nascimento else None
        cursor.execute('''
            INSERT INTO autores (id_autor, nome, data_nascimento, biografia)
            VALUES (?, ?, ?, ?)
        ''', (autor.id_autor, autor.nome, data_nasc_str, autor.biografia))
    except sqlite3.Error as e:
        print(f"Erro ao adicionar autor: {e}")
        return False
    finally:
        fechar_bd(conn)
    return True

def listar_autores_bd() -> list[Autor]:
    conn, cursor = conectar_bd()
    autores_obj = []
    try:
        cursor.execute("SELECT * FROM autores ORDER BY nome")
        autores_db = cursor.fetchall()
        for autor_row in autores_db:
            data_nasc = datetime.strptime(autor_row['data_nascimento'], '%Y-%m-%d').date() if autor_row['data_nascimento'] else None
            autores_obj.append(Autor(
                id_autor=autor_row['id_autor'],
                nome=autor_row['nome'],
                data_nascimento=data_nasc,
                biografia=autor_row['biografia']
            ))
    except sqlite3.Error as e:
        print(f"Erro ao listar autores: {e}")
    finally:
        fechar_bd(conn)
    return autores_obj

def buscar_autor_por_id_bd(id_autor: str) -> Autor | None:
    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT * FROM autores WHERE id_autor = ?", (id_autor,))
        autor_row = cursor.fetchone()
        if autor_row:
            data_nasc = datetime.strptime(autor_row['data_nascimento'], '%Y-%m-%d').date() if autor_row['data_nascimento'] else None
            return Autor(
                id_autor=autor_row['id_autor'],
                nome=autor_row['nome'],
                data_nascimento=data_nasc,
                biografia=autor_row['biografia']
            )
    except sqlite3.Error as e:
        print(f"Erro ao buscar autor: {e}")
    finally:
        fechar_bd(conn)
    return None

def adicionar_livro_bd(livro: Livro):
    conn, cursor = conectar_bd()
    try:
        cursor.execute('''
            INSERT INTO livros (id_livro, titulo, ano_publicacao, isbn, editora, numero_paginas, sinopse)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (livro.id_item, livro.titulo, livro.ano_publicacao, livro.isbn,
              livro.editora, livro.numero_paginas, livro.sinopse))

        for autor in livro.autores:
            autor_existente = buscar_autor_por_id_bd(autor.id_autor)
            if not autor_existente:
                 adicionar_autor_bd(autor)

            cursor.execute('''
                INSERT INTO livros_autores (livro_id, autor_id)
                VALUES (?, ?)
            ''', (livro.id_item, autor.id_autor))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar livro: {e}")
        conn.rollback()
        return False
    finally:
        fechar_bd(conn)


def listar_livros_bd() -> list[Livro]:
    conn, cursor = conectar_bd()
    livros_obj = []
    try:
        cursor.execute("SELECT * FROM livros ORDER BY titulo")
        livros_db = cursor.fetchall()
        for livro_row in livros_db:
            cursor.execute('''
                SELECT a.* FROM autores a
                JOIN livros_autores la ON a.id_autor = la.autor_id
                WHERE la.livro_id = ?
            ''', (livro_row['id_livro'],))
            autores_do_livro_db = cursor.fetchall()
            autores_do_livro_obj = []
            for autor_row in autores_do_livro_db:
                data_nasc = datetime.strptime(autor_row['data_nascimento'], '%Y-%m-%d').date() if autor_row['data_nascimento'] else None
                autores_do_livro_obj.append(Autor(
                    id_autor=autor_row['id_autor'],
                    nome=autor_row['nome'],
                    data_nascimento=data_nasc,
                    biografia=autor_row['biografia']
                ))
            
            livros_obj.append(Livro(
                id_livro=livro_row['id_livro'],
                titulo=livro_row['titulo'],
                ano_publicacao=livro_row['ano_publicacao'],
                isbn=livro_row['isbn'],
                editora=livro_row['editora'],
                numero_paginas=livro_row['numero_paginas'],
                sinopse=livro_row['sinopse'],
                autores=autores_do_livro_obj
            ))
    except sqlite3.Error as e:
        print(f"Erro ao listar livros: {e}")
    finally:
        fechar_bd(conn)
    return livros_obj

def buscar_livro_por_id_bd(id_livro: str) -> Livro | None:
    conn, cursor = conectar_bd()
    try:
        cursor.execute("SELECT * FROM livros WHERE id_livro = ?", (id_livro,))
        livro_row = cursor.fetchone()
        if livro_row:
            cursor.execute('''
                SELECT a.* FROM autores a
                JOIN livros_autores la ON a.id_autor = la.autor_id
                WHERE la.livro_id = ?
            ''', (livro_row['id_livro'],))
            autores_do_livro_db = cursor.fetchall()
            autores_do_livro_obj = []
            for autor_row in autores_do_livro_db:
                data_nasc = datetime.strptime(autor_row['data_nascimento'], '%Y-%m-%d').date() if autor_row['data_nascimento'] else None
                autores_do_livro_obj.append(Autor(
                    id_autor=autor_row['id_autor'],
                    nome=autor_row['nome'],
                    data_nascimento=data_nasc,
                    biografia=autor_row['biografia']
                ))

            return Livro(
                id_livro=livro_row['id_livro'],
                titulo=livro_row['titulo'],
                ano_publicacao=livro_row['ano_publicacao'],
                isbn=livro_row['isbn'],
                editora=livro_row['editora'],
                numero_paginas=livro_row['numero_paginas'],
                sinopse=livro_row['sinopse'],
                autores=autores_do_livro_obj
            )
    except sqlite3.Error as e:
        print(f"Erro ao buscar livro: {e}")
    finally:
        fechar_bd(conn)
    return None

def remover_livro_bd(id_livro: str):
    conn, cursor = conectar_bd()
    try:
        cursor.execute("DELETE FROM livros WHERE id_livro = ?", (id_livro,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao remover livro: {e}")
        conn.rollback()
        return False
    finally:
        fechar_bd(conn)
        
def atualizar_livro_bd(livro: Livro):
    conn, cursor = conectar_bd()
    try:
        cursor.execute('''
            UPDATE livros
            SET titulo = ?, ano_publicacao = ?, isbn = ?, editora = ?, numero_paginas = ?, sinopse = ?
            WHERE id_livro = ?
        ''', (livro.titulo, livro.ano_publicacao, livro.isbn, livro.editora,
              livro.numero_paginas, livro.sinopse, livro.id_item))

        cursor.execute("DELETE FROM livros_autores WHERE livro_id = ?", (livro.id_item,))
        for autor in livro.autores:
            autor_existente = buscar_autor_por_id_bd(autor.id_autor)
            if not autor_existente:
                 adicionar_autor_bd(autor)

            cursor.execute('''
                INSERT INTO livros_autores (livro_id, autor_id)
                VALUES (?, ?)
            ''', (livro.id_item, autor.id_autor))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar livro: {e}")
        conn.rollback()
        return False
    finally:
        fechar_bd(conn)

def adicionar_emprestimo_bd(emprestimo: Emprestimo):
    conn, cursor = conectar_bd()
    try:
        data_emp_str = emprestimo.data_emprestimo.isoformat()
        data_dev_prev_str = emprestimo.data_devolucao_prevista.isoformat()
        data_dev_efet_str = emprestimo.data_devolucao_efetiva.isoformat() if emprestimo.data_devolucao_efetiva else None

        cursor.execute('''
            INSERT INTO emprestimos (id_emprestimo, livro_id, nome_usuario, data_emprestimo, data_devolucao_prevista, data_devolucao_efetiva)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (emprestimo.id_emprestimo, emprestimo.livro.id_item, emprestimo.nome_usuario,
              data_emp_str, data_dev_prev_str, data_dev_efet_str))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar empréstimo: {e}")
        conn.rollback()
        return False
    finally:
        fechar_bd(conn)

def listar_emprestimos_bd() -> list[Emprestimo]:
    conn, cursor = conectar_bd()
    emprestimos_obj = []
    try:
        cursor.execute("SELECT * FROM emprestimos ORDER BY data_emprestimo DESC")
        emprestimos_db = cursor.fetchall()
        for emp_row in emprestimos_db:
            livro_obj = buscar_livro_por_id_bd(emp_row['livro_id'])
            if not livro_obj:
                print(f"Aviso: Livro com ID {emp_row['livro_id']} não encontrado para o empréstimo {emp_row['id_emprestimo']}.")
                continue

            data_emp = datetime.strptime(emp_row['data_emprestimo'], '%Y-%m-%d').date()
            data_dev_prev = datetime.strptime(emp_row['data_devolucao_prevista'], '%Y-%m-%d').date()
            data_dev_efet = datetime.strptime(emp_row['data_devolucao_efetiva'], '%Y-%m-%d').date() if emp_row['data_devolucao_efetiva'] else None
            
            emprestimo = Emprestimo(
                id_emprestimo=emp_row['id_emprestimo'],
                livro=livro_obj,
                nome_usuario=emp_row['nome_usuario'],
                data_emprestimo=data_emp,
                data_devolucao_prevista=data_dev_prev
            )
            if data_dev_efet:
                emprestimo.registrar_devolucao(data_dev_efet)

            emprestimos_obj.append(emprestimo)
            
    except sqlite3.Error as e:
        print(f"Erro ao listar empréstimos: {e}")
    finally:
        fechar_bd(conn)
    return emprestimos_obj

def atualizar_emprestimo_bd(emprestimo: Emprestimo):
    conn, cursor = conectar_bd()
    try:
        data_dev_efet_str = emprestimo.data_devolucao_efetiva.isoformat() if emprestimo.data_devolucao_efetiva else None
        cursor.execute('''
            UPDATE emprestimos
            SET data_devolucao_efetiva = ?
            WHERE id_emprestimo = ?
        ''', (data_dev_efet_str, emprestimo.id_emprestimo))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar empréstimo: {e}")
        conn.rollback()
        return False
    finally:
        fechar_bd(conn)
