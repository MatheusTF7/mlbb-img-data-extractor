#!/usr/bin/env python3
"""
Script de exemplo para testar o modo debug do MLBB Extractor.

Este script demonstra como usar o modo debug programaticamente.
"""

from pathlib import Path
from mlbb_extractor import MLBBExtractor
from mlbb_extractor.config import ExtractorConfig


def test_debug_mode():
    """Testa o modo debug com uma imagem de exemplo."""
    
    # Criar configuração com modo debug ativado
    config = ExtractorConfig()
    config.debug_mode = True
    config.debug_dir = "debug"
    
    print("=" * 60)
    print("MLBB Extractor - Teste do Modo Debug")
    print("=" * 60)
    print(f"\n🔍 Modo Debug: ATIVADO")
    print(f"📁 Diretório de debug: {config.debug_dir}/")
    print()
    
    # Criar extrator
    extractor = MLBBExtractor(config=config)
    
    # Verificar se existem imagens na pasta images/
    images_dir = Path("images")
    if not images_dir.exists():
        print("❌ Pasta 'images/' não encontrada!")
        print("   Por favor, adicione algumas imagens de screenshot do MLBB.")
        return 1
    
    # Buscar imagens
    image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ Nenhuma imagem encontrada na pasta 'images/'!")
        print("   Por favor, adicione algumas imagens de screenshot do MLBB.")
        return 1
    
    print(f"✓ Encontradas {len(image_files)} imagens")
    print()
    
    # Processar primeira imagem
    test_image = image_files[0]
    print(f"📸 Processando: {test_image.name}")
    print("-" * 60)
    
    try:
        # Extrair todos os jogadores
        results = extractor.extract_all_players(str(test_image))
        
        print(f"\n✓ Extração concluída!")
        print(f"  Jogadores extraídos: {len(results)}")
        print()
        
        # Mostrar alguns resultados
        for i, player in enumerate(results[:3], 1):
            print(f"  {i}. {player['nickname']}")
            print(f"     K/D/A: {player['kills']}/{player['deaths']}/{player['assists']}")
            print(f"     Gold: {player['gold']}")
            print(f"     Medal: {player['medal']}")
            print(f"     Ratio: {player['ratio']}")
            print()
        
        if len(results) > 3:
            print(f"  ... e mais {len(results) - 3} jogador(es)")
            print()
        
        # Informar sobre arquivos de debug
        debug_path = Path(config.debug_dir)
        if debug_path.exists():
            debug_files = list(debug_path.glob("*.png"))
            print("=" * 60)
            print("Arquivos de Debug Gerados")
            print("=" * 60)
            print(f"📂 Total: {len(debug_files)} imagens salvas em '{config.debug_dir}/'")
            print()
            print("Tipos de arquivos gerados:")
            print("  • *_result_*.png         - Detecção de VICTORY/DEFEAT")
            print("  • *_score_*.png          - Placar da partida")
            print("  • *_duration_*.png       - Duração da partida")
            print("  • *_nickname_*.png       - Nomes dos jogadores")
            print("  • *_stats_*.png          - K/D/A e Gold")
            print("  • *_ratio_*.png          - Rating de performance")
            print("  • *_medal_*.png          - Medalhas")
            print()
            print("💡 Dica: Abra as imagens para ver os cortes e processamentos!")
            print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erro ao processar imagem: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Função principal."""
    import sys
    
    print()
    result = test_debug_mode()
    print()
    
    if result == 0:
        print("✅ Teste concluído com sucesso!")
    else:
        print("❌ Teste falhou!")
    
    print()
    print("Para mais informações sobre o modo debug, consulte:")
    print("  📖 DEBUG_MODE.md")
    print()
    
    return result


if __name__ == "__main__":
    import sys
    sys.exit(main())
