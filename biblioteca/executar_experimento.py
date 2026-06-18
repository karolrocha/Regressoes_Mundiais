#!/usr/bin/env python
"""
Script para executar o experimento comparativo entre as estratégias de seleção.
"""

import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Dict, Set
import sys

# Adiciona o diretório src ao path para importar módulos
sys.path.insert(0, str(Path("src").absolute()))

# Importa as estratégias
from estrategias.selecao import EstrategiasSelecao


# ============================================================
# CONFIGURAÇÕES
# ============================================================

# Caminhos
SRC_ORIGINAL = Path("src/biblioteca.py")
SRC_BACKUP = Path("src/biblioteca_original.py")
MUTANTES_DIR = Path("mutantes")
TESTES_DIR = Path("tests")

# Lista de todos os testes (nomes)
TODOS_TESTES = [
    'test_adicionar_livro_com_sucesso',
    'test_adicionar_livro_duplicado',
    'test_remover_livro_existente',
    'test_remover_livro_inexistente',
    'test_remover_livro_emprestado',
    'test_emprestar_livro_disponivel',
    'test_emprestar_livro_indisponivel',
    'test_emprestar_livro_inexistente',
    'test_emprestar_usuario_com_limite_excedido',
    'test_devolver_livro_emprestado',
    'test_devolver_livro_nao_emprestado',
    'test_devolver_livro_com_usuario_errado',
    'test_buscar_titulo_existente',
    'test_buscar_titulo_inexistente',
    'test_buscar_titulo_case_insensitive',
    'test_buscar_titulo_exato',
    'test_buscar_titulo_contem_parcial',
    'test_listar_disponiveis',
    'test_usuario_pode_pegar_livro',
]

# Mapeamento: mutante -> métodos afetados (para cobertura)
METODOS_AFETADOS = {
    'mutante1': ['emprestar_livro'],
    'mutante2': ['devolver_livro'],
    'mutante3': ['usuario_pode_pegar_livro'],
    'mutante4': ['remover_livro'],
    'mutante5': ['buscar_por_titulo'],
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def criar_backup():
    """Cria backup do arquivo original."""
    if SRC_ORIGINAL.exists():
        shutil.copy(SRC_ORIGINAL, SRC_BACKUP)


def restaurar_original():
    """Restaura o arquivo original a partir do backup."""
    if SRC_BACKUP.exists():
        shutil.copy(SRC_BACKUP, SRC_ORIGINAL)


def aplicar_mutante(mutante_path: Path):
    """Substitui o arquivo src pelo mutante."""
    shutil.copy(mutante_path, SRC_ORIGINAL)


def rodar_testes_selecionados(selecionados: List[str]) -> tuple:
    """
    Executa apenas os testes selecionados.
    
    Args:
        selecionados: lista de nomes dos testes a executar
        
    Returns:
        (mutante_morto, tempo_execucao, saida, testes_rodados)
    """
    if not selecionados:
        return False, 0, "Nenhum teste selecionado", 0
    
    # Constrói o filtro do pytest (ex: "test1 or test2 or test3")
    filtro = " or ".join(selecionados)
    
    inicio = time.time()
    resultado = subprocess.run(
        ["python", "-m", "pytest", str(TESTES_DIR), "-k", filtro, "-v", "--tb=no"],
        capture_output=True,
        text=True
    )
    fim = time.time()
    
    # Se o pytest retornou código 0, todos os testes passaram
    testes_passaram = resultado.returncode == 0
    mutante_morto = not testes_passaram  # Se algum teste falhou, mutante foi morto
    
    # Conta quantos testes foram executados
    testes_rodados = contar_testes_executados(resultado.stdout)
    
    return mutante_morto, fim - inicio, resultado.stdout, testes_rodados


def contar_testes_executados(saida: str) -> int:
    """
    Conta quantos testes foram executados a partir da saída do pytest.
    """
    import re
    linhas = saida.split('\n')
    for linha in linhas:
        # Exemplo: "2 passed, 1 failed in 0.12s"
        if 'passed' in linha or 'failed' in linha:
            numeros = re.findall(r'\d+', linha)
            if numeros:
                return sum(int(n) for n in numeros)
    
    # Fallback: conta quantas linhas têm "PASSED" ou "FAILED"
    padrao = re.compile(r'(PASSED|FAILED)')
    return len([l for l in saida.split('\n') if padrao.search(l)])


# ============================================================
# EXPERIMENTO PRINCIPAL
# ============================================================

def main():
    print("=" * 70)
    print("EXPERIMENTO: COMPARAÇÃO DE ESTRATÉGIAS DE SELEÇÃO")
    print("=" * 70)
    print(f"Suíte de testes: {len(TODOS_TESTES)} testes")
    print()
    
    # Verifica se a pasta de mutantes existe
    if not MUTANTES_DIR.exists():
        print(f"❌ Erro: Pasta '{MUTANTES_DIR}' não encontrada!")
        print("   Crie a pasta e coloque os arquivos mutante1.py a mutante5.py")
        return
    
    # Lista os mutantes
    mutantes = sorted(MUTANTES_DIR.glob("mutante*.py"))
    if not mutantes:
        print(f"❌ Nenhum mutante encontrado em '{MUTANTES_DIR}'!")
        return
    
    print(f"Mutantes encontrados: {len(mutantes)}")
    print()
    
    # Estratégias a serem testadas
    estrategias = [
        ("Completa", EstrategiasSelecao.execucao_completa, {}),
        ("Aleatória (50%)", EstrategiasSelecao.selecao_aleatoria, {"percentual": 0.5}),
        ("Cobertura", EstrategiasSelecao.selecao_por_cobertura, {}),
    ]
    
    # Cria backup do original
    criar_backup()
    
    # Cabeçalho da tabela
    print(f"{'Mutante':<12} {'Estratégia':<18} {'Testes':<8} {'Morto?':<10} {'Tempo (s)':<10}")
    print("-" * 70)
    
    resultados = []
    
    # Para cada mutante
    for mutante in mutantes:
        nome_mutante = mutante.stem
        print(f"\n🔄 Aplicando mutante: {nome_mutante}")
        
        # Aplica o mutante
        aplicar_mutante(mutante)
        
        # Métodos afetados para cobertura
        metodos = METODOS_AFETADOS.get(nome_mutante, [])
        
        # Para cada estratégia
        for nome_estrategia, estrategia, kwargs in estrategias:
            # Prepara os argumentos
            args = kwargs.copy()
            
            # Adiciona argumentos específicos quando necessário
            if nome_estrategia == "Cobertura":
                args["metodos_afetados"] = metodos
            
            # Aplica a estratégia para selecionar os testes
            selecionados = estrategia(TODOS_TESTES, **args)
            
            # Executa os testes selecionados
            mutante_morto, tempo, saida, testes_rodados = rodar_testes_selecionados(selecionados)
            
            status = "💀 MORTO" if mutante_morto else "😵 SOBREVIVEU"
            
            # Exibe o resultado
            print(f"  {nome_estrategia:<18} {testes_rodados:<8} {status:<10} {tempo:<10.2f}")
            
            # Salva o resultado
            resultados.append({
                "mutante": nome_mutante,
                "estrategia": nome_estrategia,
                "testes_selecionados": len(selecionados),
                "testes_rodados": testes_rodados,
                "mutante_morto": mutante_morto,
                "tempo": tempo,
                "total_testes": len(TODOS_TESTES)
            })
        
        # Restaura o original para o próximo mutante
        restaurar_original()
    
    # Restaura o original no final
    restaurar_original()
    
    # ============================================================
    # RESUMO DOS RESULTADOS
    # ============================================================
    
    print("\n" + "=" * 70)
    print("RESUMO DOS RESULTADOS")
    print("=" * 70)
    
    # Para cada estratégia, mostra quantos mutantes matou
    for estrategia in set(r["estrategia"] for r in resultados):
        resultados_estrategia = [r for r in resultados if r["estrategia"] == estrategia]
        mortos = sum(1 for r in resultados_estrategia if r["mutante_morto"])
        total = len(resultados_estrategia)
        print(f"\n📊 {estrategia}: {mortos}/{total} mutantes mortos ({mortos/total*100:.1f}%)")
        
        # Mostra quais mutantes sobreviveram
        sobreviventes = [r["mutante"] for r in resultados_estrategia if not r["mutante_morto"]]
        if sobreviventes:
            print(f"   ⚠️ Sobreviveram: {', '.join(sobreviventes)}")
        else:
            print(f"   ✅ Matou todos os mutantes!")
    
    # ============================================================
    # ANÁLISE: REDUÇÃO vs EFICÁCIA
    # ============================================================
    
    print("\n" + "=" * 70)
    print("ANÁLISE: REDUÇÃO vs EFICÁCIA")
    print("=" * 70)
    
    for mutante in set(r["mutante"] for r in resultados):
        print(f"\n📘 {mutante}:")
        dados_mutante = [r for r in resultados if r["mutante"] == mutante]
        
        # Encontra o resultado da execução completa
        completo = next((r for r in dados_mutante if r["estrategia"] == "Completa"), None)
        if not completo:
            continue
        
        # Mostra cada estratégia
        for r in dados_mutante:
            if r["estrategia"] != "Completa":
                reducao = 1 - (r["testes_selecionados"] / r["total_testes"])
                status = "✅ Matou" if r["mutante_morto"] else "❌ Sobreviveu"
                print(f"   {r['estrategia']:<18} {r['testes_selecionados']}/{r['total_testes']} testes "
                      f"({reducao*100:.0f}% redução) → {status}")
    
    print("\n" + "=" * 70)
    print("✅ Experimento concluído!")
    print("=" * 70)


if __name__ == "__main__":
    main()