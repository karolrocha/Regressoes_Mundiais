import pytest
from src.biblioteca import Biblioteca, Livro


class TestBiblioteca:
    
    def setup_method(self):
        """Configura um ambiente de teste limpo antes de cada teste."""
        self.bib = Biblioteca()
        self.livro1 = Livro("978-3-16-148410-0", "Python Cookbook", "David Beazley")
        self.livro2 = Livro("978-0-596-00928-7", "Learning Python", "Mark Lutz")
        self.livro3 = Livro("978-1-491-93636-8", "Fluent Python", "Luciano Ramalho")
        
        # Adiciona livros ao acervo
        self.bib.adicionar_livro(self.livro1)
        self.bib.adicionar_livro(self.livro2)
        self.bib.adicionar_livro(self.livro3)
    
    # ========== TESTES: adicionar_livro ==========
    
    def test_adicionar_livro_com_sucesso(self):
        novo_livro = Livro("978-0-13-235088-4", "Clean Code", "Robert Martin")
        resultado = self.bib.adicionar_livro(novo_livro)
        assert resultado == True
        assert novo_livro.isbn in self.bib.acervo
    
    def test_adicionar_livro_duplicado(self):
        resultado = self.bib.adicionar_livro(self.livro1)
        assert resultado == False
    
    # ========== TESTES: remover_livro ==========
    
    def test_remover_livro_existente(self):
        resultado = self.bib.remover_livro(self.livro1.isbn)
        assert resultado == True
        assert self.livro1.isbn not in self.bib.acervo
    
    def test_remover_livro_inexistente(self):
        resultado = self.bib.remover_livro("ISBN-INEXISTENTE")
        assert resultado == False
    
    def test_remover_livro_emprestado(self):
        # Primeiro empresta o livro
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        # Tenta remover (deve falhar)
        resultado = self.bib.remover_livro(self.livro1.isbn)
        assert resultado == False
        assert self.livro1.isbn in self.bib.acervo
    
    # ========== TESTES: emprestar_livro ==========
    
    def test_emprestar_livro_disponivel(self):
        resultado = self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        assert resultado == True
        assert self.livro1.disponivel == False
        assert self.livro1.isbn in self.bib.emprestimos_ativos
    
    def test_emprestar_livro_indisponivel(self):
        # Empresta primeiro
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        # Tenta emprestar novamente (deve falhar)
        resultado = self.bib.emprestar_livro(self.livro1.isbn, "usuario2")
        assert resultado == False
    
    def test_emprestar_livro_inexistente(self):
        resultado = self.bib.emprestar_livro("ISBN-INEXISTENTE", "usuario1")
        assert resultado == False
    
    def test_emprestar_usuario_com_limite_excedido(self):
        # Cria 4 livros e tenta emprestar todos para o mesmo usuario
        livro4 = Livro("111", "Livro 4", "Autor 4")
        livro5 = Livro("222", "Livro 5", "Autor 5")
        livro6 = Livro("333", "Livro 6", "Autor 6")
        self.bib.adicionar_livro(livro4)
        self.bib.adicionar_livro(livro5)
        self.bib.adicionar_livro(livro6)
        
        # Empresta 3 livros (limite)
        self.bib.emprestar_livro(livro4.isbn, "usuario_limite")
        self.bib.emprestar_livro(livro5.isbn, "usuario_limite")
        self.bib.emprestar_livro(livro6.isbn, "usuario_limite")
        
        # Tenta emprestar o 4º (deve falhar)
        resultado = self.bib.emprestar_livro(self.livro1.isbn, "usuario_limite")
        assert resultado == False
    
    # ========== TESTES: devolver_livro ==========
    
    def test_devolver_livro_emprestado(self):
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        resultado = self.bib.devolver_livro(self.livro1.isbn, "usuario1")
        assert resultado == True
        assert self.livro1.disponivel == True
        assert self.livro1.isbn not in self.bib.emprestimos_ativos
    
    def test_devolver_livro_nao_emprestado(self):
        resultado = self.bib.devolver_livro(self.livro1.isbn, "usuario1")
        assert resultado == False
    
    def test_devolver_livro_com_usuario_errado(self):
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        resultado = self.bib.devolver_livro(self.livro1.isbn, "usuario_errado")
        assert resultado == False
    
    # ========== TESTES: buscar_por_titulo ==========
    
    def test_buscar_titulo_existente(self):
        resultado = self.bib.buscar_por_titulo("Python Cookbook")
        assert resultado is not None
        assert resultado.isbn == self.livro1.isbn
    
    def test_buscar_titulo_inexistente(self):
        resultado = self.bib.buscar_por_titulo("Titulo Inexistente")
        assert resultado is None
    
    def test_buscar_titulo_case_insensitive(self):
        resultado = self.bib.buscar_por_titulo("python cookbook")
        assert resultado is not None
        assert resultado.isbn == self.livro1.isbn
    
    # ========== TESTES: listar_disponiveis ==========
    
    def test_listar_disponiveis(self):
        disponiveis = self.bib.listar_disponiveis()
        assert len(disponiveis) == 3  # Todos disponíveis inicialmente
        
        # Empresta um livro
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        disponiveis = self.bib.listar_disponiveis()
        assert len(disponiveis) == 2
        assert self.livro1 not in disponiveis
    
    # ========== TESTES: usuario_pode_pegar_livro ==========
    
    def test_usuario_pode_pegar_livro(self):
        assert self.bib.usuario_pode_pegar_livro("usuario1") == True
        
        # Empresta 2 livros
        self.bib.emprestar_livro(self.livro1.isbn, "usuario1")
        self.bib.emprestar_livro(self.livro2.isbn, "usuario1")
        assert self.bib.usuario_pode_pegar_livro("usuario1") == True
        
        # Empresta o 3º (limite)
        self.bib.emprestar_livro(self.livro3.isbn, "usuario1")
        assert self.bib.usuario_pode_pegar_livro("usuario1") == False