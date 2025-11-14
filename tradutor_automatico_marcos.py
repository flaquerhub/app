#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Automatizador de Tradução de Comentários Patrísticos - Marcos
Apresenta arquivos sequencialmente para tradução com contexto completo
"""

import os
import sys
import json
from pathlib import Path


def ler_arquivo(caminho):
    """Lê conteúdo de um arquivo em UTF-8"""
    with open(caminho, 'r', encoding='utf-8') as f:
        return f.read()


def listar_arquivos_pendentes(diretorio_output, diretorio_traducoes):
    """Lista arquivos Marcos_X.txt que ainda não foram traduzidos"""
    arquivos_marcos = sorted([
        f for f in os.listdir(diretorio_output)
        if f.startswith('Marcos_') and f.endswith('.txt')
    ], key=lambda x: int(x.replace('Marcos_', '').replace('.txt', '')))

    # Verifica quais já foram traduzidos
    traducoes_existentes = set()
    if os.path.exists(diretorio_traducoes):
        traducoes_existentes = set([
            f for f in os.listdir(diretorio_traducoes)
            if f.startswith('marcos_') and f.endswith('_traduzido.json')
        ])

    pendentes = []
    for i, arquivo in enumerate(arquivos_marcos, start=1):
        nome_traducao = f"marcos_{i:03d}_traduzido.json"
        if nome_traducao not in traducoes_existentes:
            pendentes.append((i, arquivo, nome_traducao))

    return pendentes


def apresentar_arquivo_para_traducao(numero, arquivo_txt, prompt, exemplo_json, conteudo_arquivo):
    """Apresenta todas as informações necessárias para tradução"""

    print("\n" + "="*80)
    print(f"ARQUIVO PARA TRADUÇÃO: {numero}/47")
    print("="*80)

    print(f"\nArquivo origem: output/{arquivo_txt}")
    print(f"Arquivo destino: traducoes/marcos_{numero:03d}_traduzido.json")

    print("\n" + "-"*80)
    print("PROMPT DE TRADUÇÃO:")
    print("-"*80)
    print(prompt)

    print("\n" + "-"*80)
    print("EXEMPLO DE FORMATO JSON ESPERADO:")
    print("-"*80)
    print(exemplo_json)

    print("\n" + "-"*80)
    print("CONTEÚDO A TRADUZIR:")
    print("-"*80)
    print(conteudo_arquivo)

    print("\n" + "="*80)
    print("INSTRUÇÕES:")
    print("="*80)
    print("1. Leia o PROMPT DE TRADUÇÃO com atenção")
    print("2. Veja o EXEMPLO JSON para entender a estrutura esperada")
    print("3. Traduza o CONTEÚDO A TRADUZIR seguindo todas as diretrizes")
    print("4. Retorne APENAS o JSON válido (sem explicações adicionais)")
    print("5. O script salvará automaticamente e apresentará o próximo arquivo")
    print("="*80 + "\n")


def main():
    """Função principal"""

    # Diretórios
    dir_output = "output"
    dir_traducoes = "traducoes"

    # Cria diretório de traduções se não existir
    Path(dir_traducoes).mkdir(exist_ok=True)

    # Carrega arquivos de contexto
    try:
        prompt = ler_arquivo("prompt_traducao.txt")
        exemplo_json = ler_arquivo("bloco_001_traduzido.json")
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de contexto não encontrado: {e}")
        sys.exit(1)

    # Lista arquivos pendentes
    pendentes = listar_arquivos_pendentes(dir_output, dir_traducoes)

    if not pendentes:
        print("✓ Todos os 47 arquivos de Marcos já foram traduzidos!")
        sys.exit(0)

    print(f"\nArquivos pendentes: {len(pendentes)}/47")
    print(f"Arquivos já traduzidos: {47 - len(pendentes)}/47")
    print()

    # Pega o próximo arquivo a traduzir
    numero, arquivo_txt, nome_traducao = pendentes[0]

    # Lê o conteúdo do arquivo
    caminho_arquivo = os.path.join(dir_output, arquivo_txt)
    conteudo = ler_arquivo(caminho_arquivo)

    # Apresenta tudo para tradução
    apresentar_arquivo_para_traducao(
        numero=numero,
        arquivo_txt=arquivo_txt,
        prompt=prompt,
        exemplo_json=exemplo_json,
        conteudo_arquivo=conteudo
    )

    print(f"📋 Próximo arquivo: {arquivo_txt}")
    print(f"📝 Será salvo como: {nome_traducao}")
    print(f"📊 Progresso: {numero}/47 ({numero/47*100:.1f}%)")
    print()


if __name__ == "__main__":
    main()
