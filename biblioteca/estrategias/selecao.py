# estrategias/selecao.py

import random
from typing import List, Dict, Set


class EstrategiasSelecao:
    """
    Classe que contém as estratégias de seleção de testes de regressão.
    """
    
    @staticmethod
    def execucao_completa(suite_teste: List[str]) -> List[str]:
        """
        Estratégia 1: Execução Completa (Linha de Base)
        Retorna TODOS os testes da suíte.
        
        Args:
            suite_teste: lista com nomes de todos os testes
            
        Returns:
            Lista com todos os testes (sem redução)
        """
        return suite_teste
    
    @staticmethod
    def selecao_aleatoria(suite_teste: List[str], 
                          percentual: float = 0.5) -> List[str]:
        """
        Estratégia 2: Seleção Aleatória
        Seleciona uma porcentagem dos testes aleatoriamente.
        
        Args:
            suite_teste: lista com nomes de todos os testes
            percentual: proporção a ser selecionada (0.0 a 1.0)
            
        Returns:
            Lista com os testes selecionados aleatoriamente
        """
        if percentual <= 0:
            return []
        if percentual >= 1.0:
            return suite_teste
        
        quantidade = max(1, int(len(suite_teste) * percentual))
        return random.sample(suite_teste, quantidade)
    
    @staticmethod
    def selecao_por_cobertura(suite_teste: List[str],
                               metodos_afetados: List[str],
                               cobertura: Dict[str, Set[str]] = None) -> List[str]:
        """
        Estratégia 3: Seleção por Cobertura de Código
        Seleciona apenas os testes que cobrem os métodos afetados.
        
        Args:
            suite_teste: lista com nomes de todos os testes
            metodos_afetados: lista de métodos modificados pelo mutante
            cobertura: dicionário com nome do teste -> conjunto de métodos cobertos
            
        Returns:
            Lista com os testes que cobrem os métodos afetados
        """
        if cobertura is None:
            # Mapeamento: quais testes cobrem quais métodos
            cobertura = {
                'test_adicionar_livro_com_sucesso': {'adicionar_livro'},
                'test_adicionar_livro_duplicado': {'adicionar_livro'},
                'test_remover_livro_existente': {'remover_livro'},
                'test_remover_livro_inexistente': {'remover_livro'},
                'test_remover_livro_emprestado': {'remover_livro', 'emprestar_livro'},
                'test_emprestar_livro_disponivel': {'emprestar_livro'},
                'test_emprestar_livro_indisponivel': {'emprestar_livro'},
                'test_emprestar_livro_inexistente': {'emprestar_livro'},
                'test_emprestar_usuario_com_limite_excedido': {'emprestar_livro', 'usuario_pode_pegar_livro'},
                'test_devolver_livro_emprestado': {'devolver_livro', 'emprestar_livro'},
                'test_devolver_livro_nao_emprestado': {'devolver_livro'},
                'test_devolver_livro_com_usuario_errado': {'devolver_livro', 'emprestar_livro'},
                'test_buscar_titulo_existente': {'buscar_por_titulo'},
                'test_buscar_titulo_inexistente': {'buscar_por_titulo'},
                'test_buscar_titulo_case_insensitive': {'buscar_por_titulo'},
                'test_buscar_titulo_exato': {'buscar_por_titulo'},
                'test_buscar_titulo_contem_parcial': {'buscar_por_titulo'},
                'test_listar_disponiveis': {'listar_disponiveis'},
                'test_usuario_pode_pegar_livro': {'usuario_pode_pegar_livro'},
            }
        
        # Seleciona testes que cobrem pelo menos um método afetado
        selecionados = []
        for teste in suite_teste:
            metodos_cobertos = cobertura.get(teste, set())
            if any(metodo in metodos_cobertos for metodo in metodos_afetados):
                selecionados.append(teste)
        
        # Se nenhum teste foi selecionado, retorna todos (segurança)
        # if not selecionados:
        #     return suite_teste
        
        return selecionados