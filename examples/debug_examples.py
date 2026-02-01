"""
Exemplo de uso do modo debug via código.

Este exemplo mostra como ativar e usar o modo debug programaticamente.
"""

from pathlib import Path
from mlbb_extractor import MLBBExtractor
from mlbb_extractor.config import ExtractorConfig


def exemplo_debug_basico():
    """Exemplo básico de ativação do modo debug."""
    
    # Criar configuração
    config = ExtractorConfig()
    
    # Ativar modo debug
    config.debug_mode = True
    config.debug_dir = "debug"
    
    # Criar extrator
    extractor = MLBBExtractor(config=config)
    
    # Processar imagem
    results = extractor.extract_all_players("images/screenshot.png")
    
    print(f"Imagens de debug salvas em: {config.debug_dir}/")
    return results


def exemplo_debug_customizado():
    """Exemplo com diretório de debug customizado."""
    
    config = ExtractorConfig()
    config.debug_mode = True
    config.debug_dir = "meu_debug/analise_2026"  # Diretório customizado
    
    extractor = MLBBExtractor(config=config)
    
    # Processar
    game_data = extractor.extract_game_data("images/screenshot.png", "MTF7")
    
    if game_data:
        print(f"Jogador encontrado: {game_data.nickname}")
        print(f"Imagens salvas em: {config.debug_dir}/")
    
    return game_data


def exemplo_debug_condicional():
    """Ativa debug apenas se houver erro."""
    
    config = ExtractorConfig()
    config.debug_mode = False  # Inicialmente desligado
    
    extractor = MLBBExtractor(config=config)
    
    try:
        results = extractor.extract_all_players("images/screenshot.png")
        
        # Verificar qualidade dos resultados
        if all(player['kills'] == 0 for player in results):
            print("⚠️ Resultados suspeitos, reprocessando com debug...")
            
            # Ativar debug e reprocessar
            extractor.config.debug_mode = True
            results = extractor.extract_all_players("images/screenshot.png")
            
    except Exception as e:
        print(f"Erro detectado: {e}")
        print("Reprocessando com debug ativado...")
        
        extractor.config.debug_mode = True
        results = extractor.extract_all_players("images/screenshot.png")
    
    return results


def exemplo_debug_lote():
    """Processa múltiplas imagens com debug em lote."""
    
    config = ExtractorConfig()
    config.debug_mode = True
    config.debug_dir = "debug_lote"
    
    extractor = MLBBExtractor(config=config)
    
    # Buscar todas as imagens
    images_dir = Path("images")
    image_files = list(images_dir.glob("*.png"))
    
    all_results = []
    
    for image_file in image_files:
        print(f"Processando: {image_file.name}")
        
        # O nome da imagem será incluído automaticamente nos arquivos de debug
        results = extractor.extract_all_players(str(image_file))
        all_results.extend(results)
    
    print(f"\nTotal processado: {len(image_files)} imagens")
    print(f"Total jogadores: {len(all_results)}")
    print(f"Debug salvo em: {config.debug_dir}/")
    
    return all_results


def exemplo_debug_com_configuracao():
    """Usa arquivo de configuração com debug ativado."""
    
    # Criar configuração de arquivo
    config = ExtractorConfig("resolutions/default.json")
    
    # Ativar debug (sobrescreve valor do arquivo)
    config.debug_mode = True
    
    extractor = MLBBExtractor(config=config)
    
    results = extractor.extract_all_players("images/screenshot.png")
    
    return results


def exemplo_analise_debug():
    """Processa e analisa os arquivos de debug gerados."""
    
    config = ExtractorConfig()
    config.debug_mode = True
    config.debug_dir = "debug_analise"
    
    extractor = MLBBExtractor(config=config)
    
    # Processar
    results = extractor.extract_all_players("images/screenshot.png")
    
    # Analisar arquivos gerados
    debug_path = Path(config.debug_dir)
    
    if debug_path.exists():
        debug_files = list(debug_path.glob("*.png"))
        
        # Agrupar por tipo
        tipos = {}
        for f in debug_files:
            # Extrair tipo do nome do arquivo
            parts = f.stem.split("_")
            if len(parts) >= 4:
                tipo = parts[-2]  # Penúltimo componente (result, nickname, stats, etc.)
                tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print("\nArquivos de debug gerados:")
        print("-" * 40)
        for tipo, count in sorted(tipos.items()):
            print(f"  {tipo:20s}: {count:3d} arquivo(s)")
        print("-" * 40)
        print(f"  Total: {len(debug_files)} arquivo(s)")
    
    return results


def exemplo_debug_seletivo():
    """Ativa debug apenas para regiões específicas."""
    
    # Nota: Esta é uma demonstração conceitual
    # A implementação atual salva todas as regiões quando debug está ativo
    
    config = ExtractorConfig()
    config.debug_mode = True
    
    # Você poderia estender a classe para permitir:
    # config.debug_regions = ["result", "stats"]  # Apenas estas regiões
    
    extractor = MLBBExtractor(config=config)
    results = extractor.extract_all_players("images/screenshot.png")
    
    return results


if __name__ == "__main__":
    print("Exemplos de uso do Modo Debug")
    print("=" * 60)
    print()
    
    # Escolha um exemplo para executar
    import sys
    
    exemplos = {
        "1": ("Básico", exemplo_debug_basico),
        "2": ("Customizado", exemplo_debug_customizado),
        "3": ("Condicional", exemplo_debug_condicional),
        "4": ("Lote", exemplo_debug_lote),
        "5": ("Com Configuração", exemplo_debug_com_configuracao),
        "6": ("Análise", exemplo_analise_debug),
    }
    
    print("Escolha um exemplo:")
    for key, (nome, _) in exemplos.items():
        print(f"  {key}. {nome}")
    print()
    
    escolha = input("Digite o número (ou Enter para exemplo básico): ").strip()
    
    if not escolha:
        escolha = "1"
    
    if escolha in exemplos:
        nome, funcao = exemplos[escolha]
        print(f"\nExecutando: {nome}")
        print("-" * 60)
        print()
        
        try:
            resultado = funcao()
            print()
            print("✅ Exemplo executado com sucesso!")
        except FileNotFoundError as e:
            print(f"\n❌ Erro: {e}")
            print("\nDica: Adicione imagens de screenshot na pasta 'images/'")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Opção inválida!")
        sys.exit(1)
