#!/usr/bin/env python3
"""
MLBB Image Data Extractor - Interface de Linha de Comando

Este script extrai dados de jogadores de screenshots de final de partida
do Mobile Legends Bang Bang.

Modos de Operação:
1. Busca por jogador específico (-p/--player)
2. Extração de todos os jogadores (--all-players)

Exemplos de Uso:
    # Extrair dados de um jogador específico
    python main.py -i screenshot.png -p "MTF7"
    
    # Extrair todos os jogadores
    python main.py -i screenshot.png --all-players
    
    # Com caminho do Tesseract (se não estiver no PATH)
    python main.py -i screenshot.png -p "MTF7" --tesseract-cmd "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    
    # Com arquivo de configuração personalizado
    python main.py -i screenshot.png --all-players --config config.json
    
    # Gerar arquivo de configuração de exemplo
    python main.py --generate-config
"""

import argparse
import sys
import json
from pathlib import Path

from mlbb_extractor import MLBBExtractor
from mlbb_extractor.config import ExtractorConfig


def main():
    """Função principal da CLI."""
    parser = argparse.ArgumentParser(
        description="Extrai dados de jogadores de screenshots do MLBB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Extrair dados de um jogador específico
  python main.py -i screenshot.png -p MTF7

  # Extrair todos os jogadores do time
  python main.py -i screenshot.png --all-players

  # Especificar caminho do Tesseract
  python main.py -i screenshot.png -p MTF7 --tesseract-cmd "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

  # Usar arquivo de configuração
  python main.py -i screenshot.png --all-players --config config.json

  # Gerar arquivo de configuração de exemplo
  python main.py --generate-config
        """
    )
    
    # Opções de entrada
    parser.add_argument(
        "-i", "--image",
        help="Caminho para a imagem do screenshot",
    )
    
    # Opções de extração de jogador
    player_group = parser.add_mutually_exclusive_group()
    player_group.add_argument(
        "-p", "--player",
        help="Nickname do jogador a ser buscado",
    )
    player_group.add_argument(
        "--all-players",
        action="store_true",
        help="Extrair dados de todos os 5 jogadores do time aliado",
    )
    
    # Opções de saída
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Diretório de saída (padrão: output)",
    )
    parser.add_argument(
        "-n", "--name",
        default="player_stats",
        help="Nome base para os arquivos de saída (padrão: player_stats)",
    )
    
    # Opções de configuração
    parser.add_argument(
        "--config",
        help="Caminho para arquivo de configuração JSON",
    )
    parser.add_argument(
        "--tesseract-cmd",
        help="Caminho para o executável do Tesseract (se não estiver no PATH)",
    )
    parser.add_argument(
        "--profile",
        help="Nome do perfil de resolução a ser usado",
    )
    
    # Utilitários
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Gera um arquivo de configuração de exemplo",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="Lista os perfis de resolução disponíveis",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativa saída de debug",
    )
    
    args = parser.parse_args()
    
    # Comandos utilitários
    if args.generate_config:
        return generate_config()
    
    if args.list_profiles:
        return list_profiles(args.config)
    
    # Validação de argumentos
    if not args.image:
        parser.error("O argumento -i/--image é obrigatório para extração de dados")
    
    if not args.player and not args.all_players:
        parser.error("Especifique -p/--player para buscar um jogador ou --all-players para todos")
    
    # Executar extração
    return extract_data(args)


def generate_config() -> int:
    """Gera um arquivo de configuração de exemplo."""
    config = ExtractorConfig()
    output_path = "config.json"
    config.save_to_file(output_path)
    
    print(f"Arquivo de configuração gerado: {output_path}")
    print("\nO arquivo contém:")
    print("- Perfil padrão para resolução 2400x1080")
    print("- Configurações de Tesseract e diretório de saída")
    print("\nEdite o arquivo para adicionar novos perfis de resolução")
    print("ou ajustar as coordenadas das regiões.")
    
    return 0


def list_profiles(config_path: str = None) -> int:
    """Lista os perfis de resolução disponíveis."""
    config = ExtractorConfig(config_path)
    
    print("Perfis de Resolução Disponíveis:")
    print("=" * 50)
    
    for name in config.list_profiles():
        profile = config.profiles[name]
        active = " (ativo)" if name == config.active_profile_name else ""
        print(f"\n{name}{active}")
        print(f"  Descrição: {profile.description}")
        print(f"  Resolução de referência: {profile.reference_width}x{profile.reference_height}")
    
    return 0


def extract_data(args) -> int:
    """
    Executa a extração de dados.
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        Código de saída (0 = sucesso, 1 = erro)
    """
    try:
        # Carregar configuração
        config = None
        if args.config:
            config = ExtractorConfig(args.config)
        
        # Criar extrator
        extractor = MLBBExtractor(
            tesseract_cmd=args.tesseract_cmd,
            config=config
        )
        
        # Definir perfil se especificado
        if args.profile:
            extractor.config.set_active_profile(args.profile)
        
        print(f"Processando imagem: {args.image}")
        
        if args.all_players:
            return extract_all_players(extractor, args)
        else:
            return extract_single_player(extractor, args)
            
    except FileNotFoundError as e:
        print(f"\nErro: Arquivo não encontrado - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nErro: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def extract_single_player(extractor: MLBBExtractor, args) -> int:
    """
    Extrai dados de um jogador específico.
    
    Args:
        extractor: Instância do MLBBExtractor
        args: Argumentos da linha de comando
        
    Returns:
        Código de saída
    """
    print(f"Buscando jogador: {args.player}")
    
    game_data = extractor.extract_game_data(args.image, args.player)
    
    if game_data is None:
        print(f"\nJogador '{args.player}' não encontrado no screenshot.")
        print("Certifique-se de que o nickname está correto (matches parciais são suportados).")
        return 1
    
    # Exibir resultados
    print("\n" + "=" * 50)
    print("Extração Completa!")
    print("=" * 50)
    
    result_dict = game_data.to_dict()
    
    print(f"\nJogador: {result_dict['nickname']}")
    print(f"  Kills: {result_dict['kills']}")
    print(f"  Deaths: {result_dict['deaths']}")
    print(f"  Assists: {result_dict['assists']}")
    print(f"  Ouro: {result_dict['gold']}")
    print(f"  Rating: {result_dict['ratio']}")
    print(f"  Medalha: {result_dict['medal']}")
    print(f"\nInformações da Partida:")
    print(f"  Resultado: {result_dict['result']}")
    print(f"  Placar: {result_dict['my_team_score']} - {result_dict['adversary_team_score']}")
    print(f"  Duração: {result_dict['duration']}")
    
    # Exportar
    output_path = export_json(result_dict, args.output, args.name)
    print(f"\nExportado para: {output_path}")
    
    return 0


def extract_all_players(extractor: MLBBExtractor, args) -> int:
    """
    Extrai dados de todos os jogadores.
    
    Args:
        extractor: Instância do MLBBExtractor
        args: Argumentos da linha de comando
        
    Returns:
        Código de saída
    """
    print("Extraindo dados de todos os jogadores do time aliado...")
    
    results = extractor.extract_all_players(args.image)
    
    if not results:
        print("Nenhum dado de jogador pôde ser extraído.")
        return 1
    
    # Exibir resultados
    print("\n" + "=" * 50)
    print("Extração Completa!")
    print("=" * 50)
    
    for player_data in results:
        print(f"\nJogador {player_data['position']}: {player_data['nickname']}")
        print(f"  K/D/A: {player_data['kills']}/{player_data['deaths']}/{player_data['assists']}")
        print(f"  Ouro: {player_data['gold']}")
        print(f"  Rating: {player_data['ratio']}")
        print(f"  Medalha: {player_data['medal']}")
    
    # Informações da partida (do primeiro jogador)
    if results:
        print(f"\nInformações da Partida:")
        print(f"  Resultado: {results[0]['result']}")
        print(f"  Placar: {results[0]['my_team_score']} - {results[0]['adversary_team_score']}")
        print(f"  Duração: {results[0]['duration']}")
    
    # Exportar
    output_path = export_json(results, args.output, args.name)
    print(f"\nExportado para: {output_path}")
    
    return 0


def export_json(data, output_dir: str, filename: str) -> str:
    """
    Exporta dados para arquivo JSON.
    
    Args:
        data: Dados a serem exportados
        output_dir: Diretório de saída
        filename: Nome base do arquivo
        
    Returns:
        Caminho do arquivo exportado
    """
    output_path = Path(output_dir) / f"{filename}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(output_path)


if __name__ == "__main__":
    sys.exit(main())
