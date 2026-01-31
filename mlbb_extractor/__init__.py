"""
MLBB Image Data Extractor

Biblioteca Python para extração de dados estruturados de screenshots de
final de partida do Mobile Legends Bang Bang usando OpenCV e Tesseract OCR.

Uso Básico:
    from mlbb_extractor import MLBBExtractor
    
    # Criar extrator
    extractor = MLBBExtractor(tesseract_cmd="caminho/para/tesseract")
    
    # Buscar dados de um jogador específico
    game_data = extractor.extract_game_data("screenshot.png", "NicknameJogador")
    
    # Extrair todos os jogadores
    all_players = extractor.extract_all_players("screenshot.png")

Classes Principais:
    MLBBExtractor: Classe principal para extração de dados
    ExtractorConfig: Gerenciador de configuração e perfis de resolução
    GameData: Dados completos do jogo para um jogador
    PlayerStats: Estatísticas de um jogador
    MatchInfo: Informações da partida
"""

__version__ = "1.0.0"

from .extractor.mlbb_extractor import (
    MLBBExtractor,
    GameData,
    PlayerStats,
    MatchInfo,
    MedalType,
)
from .config import (
    ExtractorConfig,
    ResolutionProfile,
    RegionConfig,
    PlayerRegionConfig,
    DEFAULT_PROFILE,
)
from .preprocessor.image_processor import ImagePreprocessor

__all__ = [
    # Classes principais
    "MLBBExtractor",
    "ExtractorConfig",
    
    # Data classes
    "GameData",
    "PlayerStats",
    "MatchInfo",
    "MedalType",
    
    # Configuração
    "ResolutionProfile",
    "RegionConfig",
    "PlayerRegionConfig",
    "DEFAULT_PROFILE",
    
    # Utilitários
    "ImagePreprocessor",
]

