#!/usr/bin/env python3
"""
Script de teste para validar a extração de heróis.

Este script testa:
1. Se o heroes_map.json é carregado corretamente
2. Se as imagens de heróis são carregadas com features ORB
3. Se a extração de herói funciona com uma imagem de teste
"""

from pathlib import Path
from mlbb_extractor import MLBBExtractor


def test_heroes_loading():
    """Testa o carregamento do heroes_map e das imagens."""
    print("=" * 60)
    print("TESTE: Carregamento de Heróis")
    print("=" * 60)
    
    extractor = MLBBExtractor()
    
    print(f"\n✓ Heroes map carregado: {len(extractor.heroes_map)} heróis")
    for hero_name, hero_path in extractor.heroes_map.items():
        print(f"  - {hero_name}: {hero_path}")
    
    print(f"\n✓ Imagens de heróis com features ORB: {len(extractor.hero_images)} imagens")
    for hero_name, hero_data in extractor.hero_images.items():
        n_keypoints = len(hero_data['keypoints'])
        print(f"  - {hero_name}: {n_keypoints} keypoints")
    
    if len(extractor.heroes_map) != len(extractor.hero_images):
        missing = set(extractor.heroes_map.keys()) - set(extractor.hero_images.keys())
        if missing:
            print(f"\n⚠ Aviso: {len(missing)} heróis no map sem imagem carregada:")
            for hero in missing:
                print(f"  - {hero}")
    
    return extractor


def test_hero_extraction():
    """Testa a extração de herói em uma imagem."""
    print("\n" + "=" * 60)
    print("TESTE: Extração de Herói de Imagem")
    print("=" * 60)
    
    # Procurar imagens de teste
    images_dir = Path("images")
    if not images_dir.exists():
        print("\n⚠ Diretório 'images/' não encontrado. Pulando teste de extração.")
        return
    
    test_images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))
    
    if not test_images:
        print("\n⚠ Nenhuma imagem de teste encontrada em 'images/'. Pulando teste de extração.")
        return
    
    # Usar primeira imagem encontrada
    test_image = test_images[0]
    print(f"\nTestando com imagem: {test_image.name}")
    
    extractor = MLBBExtractor()
    
    try:
        results = extractor.extract_all_players(str(test_image))
        
        print(f"\n✓ Extração concluída!")
        print(f"\nResultado da partida: {results['result']}")
        print(f"Placar: {results['my_team_score']} x {results['adversary_team_score']}")
        print(f"Duração: {results['duration']}")
        
        print(f"\n{'='*60}")
        print("JOGADORES DO MEU TIME:")
        print(f"{'='*60}")
        
        heroes_found = 0
        for player in results['my_team']:
            hero_status = player['hero'] if player['hero'] != "NO_MATCH" else "(não identificado)"
            if player['hero'] != "NO_MATCH":
                heroes_found += 1
            
            print(f"\nPosição {player['position']}:")
            print(f"  Nickname: {player['nickname']}")
            print(f"  Herói: {hero_status}")
            print(f"  K/D/A: {player['kills']}/{player['deaths']}/{player['assists']}")
            print(f"  Ouro: {player['gold']}")
            print(f"  Medalha: {player['medal']}")
            print(f"  Rating: {player['ratio']}")
            if player['is_mvp']:
                print(f"  ⭐ MVP")
        
        print(f"\n{'='*60}")
        print(f"RESUMO: {heroes_found}/5 heróis identificados")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n✗ Erro durante extração: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTE DE EXTRAÇÃO DE HERÓIS - MLBB Image Data Extractor")
    print("Método: ORB Feature Matching + Histograma de Cores")
    print("=" * 60)
    
    # Teste 1: Carregamento
    extractor = test_heroes_loading()
    
    # Teste 2: Extração (se houver imagens)
    test_hero_extraction()
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)


if __name__ == "__main__":
    main()
