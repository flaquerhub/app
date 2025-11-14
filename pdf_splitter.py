#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para dividir PDFs de comentários patrísticos da Bíblia
Mantém a integridade dos blocos de comentários versículo a versículo
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai texto de um arquivo PDF

    Args:
        pdf_path: Caminho para o arquivo PDF

    Returns:
        Texto extraído do PDF
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        sys.exit(1)


def detect_book_name(text: str) -> str:
    """
    Detecta o nome do livro bíblico no texto
    Procura por padrões como "2 Juan 1:1", "Lucas 1:1", "Mateo 1:1", etc.

    Args:
        text: Texto extraído do PDF

    Returns:
        Nome do livro detectado
    """
    # Padrão para detectar referências bíblicas (nome do livro + capítulo:versículo)
    pattern = r'([1-3]?\s*[A-Za-zÁÉÍÓÚáéíóúñÑ]+)\s+\d+:\d+'

    matches = re.findall(pattern, text)
    if matches:
        # Pega o primeiro match e limpa espaços extras
        book_name = matches[0].strip()
        return book_name

    return "Libro"  # Fallback se não detectar


def split_into_blocks(text: str, book_name: str) -> List[Tuple[str, str]]:
    """
    Divide o texto em blocos baseado nas referências bíblicas
    Cada bloco vai desde uma referência até a próxima

    Args:
        text: Texto completo extraído
        book_name: Nome do livro bíblico

    Returns:
        Lista de tuplas (referência, conteúdo_do_bloco)
    """
    # Padrão para detectar início de um bloco (referência bíblica)
    # Ex: "2 Juan 1:5", "2 Juan 1:4-6", etc.
    pattern = rf'{re.escape(book_name)}\s+\d+:\d+(?:-\d+)?'

    # Encontra todas as posições das referências
    matches = list(re.finditer(pattern, text))

    if not matches:
        print(f"AVISO: Nenhuma referência encontrada para '{book_name}'")
        return []

    blocks = []

    for i, match in enumerate(matches):
        reference = match.group()
        start_pos = match.start()

        # Fim é o início da próxima referência, ou fim do texto
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(text)

        block_content = text[start_pos:end_pos].strip()
        blocks.append((reference, block_content))

    return blocks


def should_skip_block(block_content: str) -> bool:
    """
    Verifica se o bloco deve ser ignorado (tipo 2)
    Blocos com "Descripción general" ou "Introducción general" são ignorados

    Args:
        block_content: Conteúdo do bloco

    Returns:
        True se deve ser ignorado, False caso contrário
    """
    # Verifica se contém "Descripción general" ou "Introducción general"
    skip_patterns = [
        r'Descripci[oó]n\s+general',
        r'Introducci[oó]n\s+general'
    ]

    for pattern in skip_patterns:
        if re.search(pattern, block_content, re.IGNORECASE):
            return True

    return False


def split_blocks_by_size(blocks: List[Tuple[str, str]], max_chars: int = 15000) -> List[List[Tuple[str, str]]]:
    """
    Divide blocos em grupos de aproximadamente max_chars caracteres
    Nunca quebra um bloco no meio - sempre completa o bloco atual

    Args:
        blocks: Lista de tuplas (referência, conteúdo)
        max_chars: Número máximo de caracteres por arquivo

    Returns:
        Lista de listas de blocos
    """
    result = []
    current_group = []
    current_size = 0

    for reference, content in blocks:
        block_size = len(content)

        # Se adicionar este bloco ultrapassar o limite E já temos blocos no grupo atual
        if current_size + block_size > max_chars and current_group:
            # Salva o grupo atual e inicia um novo
            result.append(current_group)
            current_group = [(reference, content)]
            current_size = block_size
        else:
            # Adiciona ao grupo atual
            current_group.append((reference, content))
            current_size += block_size

    # Adiciona o último grupo se não estiver vazio
    if current_group:
        result.append(current_group)

    return result


def save_split_files(groups: List[List[Tuple[str, str]]], original_filename: str, output_dir: str = "."):
    """
    Salva os grupos de blocos em arquivos separados

    Args:
        groups: Lista de grupos de blocos
        original_filename: Nome do arquivo original (sem extensão)
        output_dir: Diretório de saída
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for i, group in enumerate(groups, start=1):
        filename = f"{original_filename}_{i}.txt"
        filepath = output_path / filename

        # Junta todos os blocos do grupo
        content = "\n\n".join([block_content for _, block_content in group])

        # Salva com encoding UTF-8 para preservar caracteres especiais
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Estatísticas
        total_chars = len(content)
        num_blocks = len(group)
        first_ref = group[0][0]
        last_ref = group[-1][0]

        print(f"✓ Criado: {filename}")
        print(f"  - Blocos: {num_blocks}")
        print(f"  - Caracteres: {total_chars:,}")
        print(f"  - Referências: {first_ref} até {last_ref}")
        print()


def process_pdf(pdf_path: str, output_dir: str = ".", max_chars: int = 15000):
    """
    Processa um PDF completo: extrai, divide e salva

    Args:
        pdf_path: Caminho para o arquivo PDF
        output_dir: Diretório de saída
        max_chars: Tamanho máximo por arquivo
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        print(f"ERRO: Arquivo não encontrado: {pdf_path}")
        sys.exit(1)

    if not pdf_file.suffix.lower() == '.pdf':
        print(f"ERRO: O arquivo deve ser um PDF: {pdf_path}")
        sys.exit(1)

    print(f"Processando: {pdf_file.name}")
    print("=" * 60)

    # 1. Extrai texto do PDF
    print("1. Extraindo texto do PDF...")
    text = extract_text_from_pdf(pdf_path)
    print(f"   Total de caracteres extraídos: {len(text):,}")

    # 2. Detecta o nome do livro
    print("\n2. Detectando nome do livro...")
    book_name = detect_book_name(text)
    print(f"   Livro detectado: '{book_name}'")

    # 3. Divide em blocos
    print("\n3. Dividindo em blocos...")
    all_blocks = split_into_blocks(text, book_name)
    print(f"   Total de blocos encontrados: {len(all_blocks)}")

    # 4. Filtra blocos (remove "Descripción general")
    print("\n4. Filtrando blocos...")
    filtered_blocks = []
    skipped_count = 0

    for reference, content in all_blocks:
        if should_skip_block(content):
            skipped_count += 1
            print(f"   ✗ Ignorado: {reference} (Descripción/Introducción general)")
        else:
            filtered_blocks.append((reference, content))

    print(f"   Blocos mantidos: {len(filtered_blocks)}")
    print(f"   Blocos ignorados: {skipped_count}")

    if not filtered_blocks:
        print("\nERRO: Nenhum bloco válido encontrado após filtragem!")
        sys.exit(1)

    # 5. Agrupa por tamanho
    print(f"\n5. Agrupando blocos (máximo ~{max_chars:,} caracteres)...")
    groups = split_blocks_by_size(filtered_blocks, max_chars)
    print(f"   Total de arquivos a criar: {len(groups)}")

    # 6. Salva arquivos
    print(f"\n6. Salvando arquivos em '{output_dir}'...")
    print()
    original_name = pdf_file.stem
    save_split_files(groups, original_name, output_dir)

    print("=" * 60)
    print("✓ Processamento concluído com sucesso!")
    print(f"✓ {len(groups)} arquivo(s) criado(s)")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python pdf_splitter.py <arquivo.pdf> [diretorio_saida] [tamanho_max]")
        print()
        print("Exemplos:")
        print("  python pdf_splitter.py '2 Juan.pdf'")
        print("  python pdf_splitter.py '2 Juan.pdf' output")
        print("  python pdf_splitter.py '2 Juan.pdf' output 20000")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 15000

    process_pdf(pdf_path, output_dir, max_chars)


if __name__ == "__main__":
    main()
