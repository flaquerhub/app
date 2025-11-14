#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para salvar tradução e apresentar o próximo arquivo
Uso: python3 salvar_e_continuar.py <numero_bloco> '<json_traduzido>'
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def salvar_traducao(numero, json_content):
    """Salva a tradução em JSON"""
    dir_traducoes = "traducoes"
    Path(dir_traducoes).mkdir(exist_ok=True)

    nome_arquivo = f"bloco_{numero:03d}_traduzido.json"
    caminho = os.path.join(dir_traducoes, nome_arquivo)

    # Valida JSON
    try:
        dados = json.loads(json_content)
        # Reescreve com indentação bonita
        json_formatado = json.dumps(dados, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        print(f"❌ ERRO: JSON inválido!")
        print(f"   {e}")
        return False

    # Salva o arquivo
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json_formatado)

    print(f"✓ Tradução salva: {nome_arquivo}")
    return True


def fazer_commit_se_necessario(numero):
    """Faz commit a cada 10 arquivos traduzidos"""
    if numero % 10 == 0:
        print(f"\n📦 Fazendo commit dos últimos 10 arquivos...")
        try:
            subprocess.run([
                "git", "add", "traducoes/"
            ], check=True)

            mensagem = f"Add traduções de Lucas - blocos {numero-9:03d} a {numero:03d}"
            subprocess.run([
                "git", "commit", "-m", mensagem
            ], check=True)

            print(f"✓ Commit realizado: {mensagem}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Aviso: Erro ao fazer commit: {e}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 salvar_e_continuar.py <numero_bloco> '<json_traduzido>'")
        print("\nExemplo:")
        print('  python3 salvar_e_continuar.py 1 \'{"livro": "Lucas", ...}\'')
        sys.exit(1)

    numero = int(sys.argv[1])
    json_content = sys.argv[2]

    # Salva a tradução
    if not salvar_traducao(numero, json_content):
        sys.exit(1)

    # Faz commit se necessário
    fazer_commit_se_necessario(numero)

    # Calcula estatísticas
    total = 91
    restantes = total - numero
    percentual = (numero / total) * 100

    print()
    print("="*60)
    print(f"✓ Progresso: {numero}/{total} ({percentual:.1f}%)")
    print(f"  Restantes: {restantes} arquivos")
    print("="*60)

    if restantes > 0:
        print()
        print("🔄 Executando tradutor_automatico.py para o próximo arquivo...")
        print()
        subprocess.run(["python3", "tradutor_automatico.py"])
    else:
        print()
        print("🎉 TODAS AS TRADUÇÕES DE LUCAS FORAM CONCLUÍDAS!")
        print()


if __name__ == "__main__":
    main()
