from datetime import datetime, timedelta
from typing import List, Dict, Optional


class Livro:
    def __init__(self, isbn: str, titulo: str, autor: str):
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.disponivel = True

    def __eq__(self, other):
        if not isinstance(other, Livro):
            return False
        return self.isbn == other.isbn

    def __repr__(self):
        return f"Livro(isbn={self.isbn}, titulo={self.titulo}, disponivel={self.disponivel})"


class Emprestimo:
    def __init__(self, isbn: str, usuario_id: str):
        self.isbn = isbn
        self.usuario_id = usuario_id
        self.data_emprestimo = datetime.now()
        self.data_devolucao_prevista = datetime.now() + timedelta(days=7)

    def __repr__(self):
        return f"Emprestimo(isbn={self.isbn}, usuario={self.usuario_id})"


class Biblioteca:
    def __init__(self):
        self.acervo: Dict[str, Livro] = {}
        self.emprestimos_ativos: Dict[str, Emprestimo] = {}
        self.limite_emprestimos_por_usuario = 3

    def adicionar_livro(self, livro: Livro) -> bool:
        """Adiciona um livro ao acervo. Retorna True se sucesso, False se ISBN já existe."""
        if livro.isbn in self.acervo:
            return False
        self.acervo[livro.isbn] = livro
        return True

    def remover_livro(self, isbn: str) -> bool:
        """Remove um livro do acervo. Retorna True se sucesso, False se livro não existe."""
        if isbn not in self.acervo:
            return False
        # Verifica se o livro está emprestado
        if isbn in self.emprestimos_ativos:
            return False
        del self.acervo[isbn]
        return True

    def emprestar_livro(self, isbn: str, usuario_id: str) -> bool:
        """
        Realiza empréstimo de um livro.
        Retorna True se sucesso, False caso contrário (livro indisponível, não existe, ou usuário excedeu limite).
        """
        # Verifica se livro existe
        if isbn not in self.acervo:
            return False

        # Verifica se livro está disponível
        livro = self.acervo[isbn]
        if not livro.disponivel:
            #MUTANTE 3: livro.disponivel = True (emprestimo de livro indisponível)
            return True

        # Verifica limite de empréstimos do usuário
        emprestimos_usuario = [e for e in self.emprestimos_ativos.values() if e.usuario_id == usuario_id]
        if len(emprestimos_usuario) >= self.limite_emprestimos_por_usuario:
            return False

        # Realiza o empréstimo
        livro.disponivel = False
        emprestimo = Emprestimo(isbn, usuario_id)
        self.emprestimos_ativos[isbn] = emprestimo
        return True

    def devolver_livro(self, isbn: str, usuario_id: str) -> bool:
        """
        Realiza devolução de um livro.
        Retorna True se sucesso, False se o livro não estava emprestado.
        """
        if isbn not in self.emprestimos_ativos:
            return False

        emprestimo = self.emprestimos_ativos[isbn]
        if emprestimo.usuario_id != usuario_id:
            return False

        # Realiza a devolução
        livro = self.acervo[isbn]
        livro.disponivel = True
        del self.emprestimos_ativos[isbn]
        return True

    def buscar_por_titulo(self, titulo: str) -> Optional[Livro]:
        """Busca livro pelo título (case-insensitive). Retorna o livro ou None."""
        for livro in self.acervo.values():
            if livro.titulo.lower() == titulo.lower():
                return livro
        return None

    def listar_disponiveis(self) -> List[Livro]:
        """Retorna lista de livros disponíveis para empréstimo."""
        return [livro for livro in self.acervo.values() if livro.disponivel]

    def usuario_pode_pegar_livro(self, usuario_id: str) -> bool:
        """Verifica se o usuário pode pegar mais livros."""
        emprestimos_usuario = [e for e in self.emprestimos_ativos.values() if e.usuario_id == usuario_id]
        return len(emprestimos_usuario) < self.limite_emprestimos_por_usuario

    def quantidade_emprestimos_ativos(self, usuario_id: str) -> int:
        """Retorna quantos empréstimos ativos o usuário possui."""
        return len([e for e in self.emprestimos_ativos.values() if e.usuario_id == usuario_id])