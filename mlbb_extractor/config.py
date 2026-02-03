"""
Configuração do MLBB Image Data Extractor.

Este módulo gerencia as configurações de resolução e regiões para extração
de dados de screenshots do Mobile Legends Bang Bang.

As coordenadas são definidas em porcentagem (0-100) para manter responsividade
entre diferentes resoluções de imagem.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class RegionConfig:
    """Configuração de uma região na imagem."""
    x: float  # Posição X em porcentagem (0-100)
    y: float  # Posição Y em porcentagem (0-100)
    w: float  # Largura em porcentagem
    h: float  # Altura em porcentagem

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)
    
    def to_pixels(self, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
        """Converte coordenadas de porcentagem para pixels."""
        px_x = int((self.x / 100) * image_width)
        px_y = int((self.y / 100) * image_height)
        px_w = int((self.w / 100) * image_width)
        px_h = int((self.h / 100) * image_height)
        return (px_x, px_y, px_w, px_h)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "RegionConfig":
        return cls(**data)


@dataclass
class PlayerRegionConfig:
    """Configuração das regiões de um jogador."""
    nickname: RegionConfig
    stats: RegionConfig
    medal: RegionConfig
    ratio: RegionConfig
    hero: Optional[RegionConfig] = None

    def to_dict(self) -> Dict[str, Dict[str, float]]:
        result = {
            "nickname": self.nickname.to_dict(),
            "stats": self.stats.to_dict(),
            "medal": self.medal.to_dict(),
            "ratio": self.ratio.to_dict(),
        }
        if self.hero:
            result["hero"] = self.hero.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, float]]) -> "PlayerRegionConfig":
        return cls(
            nickname=RegionConfig.from_dict(data["nickname"]),
            stats=RegionConfig.from_dict(data["stats"]),
            medal=RegionConfig.from_dict(data["medal"]),
            ratio=RegionConfig.from_dict(data["ratio"]),
            hero=RegionConfig.from_dict(data["hero"]) if "hero" in data else None,
        )


@dataclass
class ResolutionProfile:
    """
    Perfil de resolução com todas as regiões configuradas.
    
    Cada perfil define as coordenadas das regiões para uma resolução específica.
    As coordenadas são em porcentagem para serem aplicáveis a imagens similares.
    """
    name: str
    description: str
    reference_width: int  # Largura de referência em pixels
    reference_height: int  # Altura de referência em pixels
    
    # Regiões de informações da partida
    result_region: RegionConfig
    my_team_score_region: RegionConfig
    adversary_score_region: RegionConfig
    duration_region: RegionConfig
    
    # Regiões dos 5 jogadores
    players: List[PlayerRegionConfig] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "reference_width": self.reference_width,
            "reference_height": self.reference_height,
            "result_region": self.result_region.to_dict(),
            "my_team_score_region": self.my_team_score_region.to_dict(),
            "adversary_score_region": self.adversary_score_region.to_dict(),
            "duration_region": self.duration_region.to_dict(),
            "players": [p.to_dict() for p in self.players],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResolutionProfile":
        return cls(
            name=data["name"],
            description=data["description"],
            reference_width=data["reference_width"],
            reference_height=data["reference_height"],
            result_region=RegionConfig.from_dict(data["result_region"]),
            my_team_score_region=RegionConfig.from_dict(data["my_team_score_region"]),
            adversary_score_region=RegionConfig.from_dict(data["adversary_score_region"]),
            duration_region=RegionConfig.from_dict(data["duration_region"]),
            players=[PlayerRegionConfig.from_dict(p) for p in data["players"]],
        )


# =============================================================================
# PERFIL PADRÃO - 2400x1080 (20:9 ultrawide)
# =============================================================================

DEFAULT_PROFILE = ResolutionProfile(
    name="default_2400x1080",
    description="Perfil padrão para resolução 2400x1080 (20:9 ultrawide)",
    reference_width=2400,
    reference_height=1080,
    
    # Regiões de informações da partida
    result_region=RegionConfig(x=40.02, y=3.11, w=19.90, h=10.68),
    my_team_score_region=RegionConfig(x=32.48, y=5.09, w=4.97, h=8.57),
    adversary_score_region=RegionConfig(x=62.60, y=5.22, w=4.81, h=7.95),
    duration_region=RegionConfig(x=77.25, y=11.43, w=4.58, h=4.10),
    
    # Regiões dos 5 jogadores
    players=[
        # Player 1
        PlayerRegionConfig(
            nickname=RegionConfig(x=21.07, y=20.80, w=10.56, h=5.88),
            stats=RegionConfig(x=31.13, y=21.99, w=12.13, h=4.22),
            medal=RegionConfig(x=43.77, y=22.61, w=3.86, h=7.45),
            ratio=RegionConfig(x=43.77, y=29.32, w=3.86, h=4.22),
            hero=RegionConfig(x=14.195397835773393, y=21.82711456859972, w=4.894818586887333, h=10.726364922206507),
        ),
        # Player 2
        PlayerRegionConfig(
            nickname=RegionConfig(x=20.96, y=33.59, w=10.56, h=5.88),
            stats=RegionConfig(x=31.19, y=34.53, w=12.13, h=4.22),
            medal=RegionConfig(x=43.82, y=35.16, w=3.86, h=7.58),
            ratio=RegionConfig(x=43.71, y=42.24, w=3.86, h=4.22),
            hero=RegionConfig(x=14.212705283259071, y=34.49711456859972, w=4.831164863144494, h=10.726364922206507),
        ),
        # Player 3
        PlayerRegionConfig(
            nickname=RegionConfig(x=20.96, y=46.49, w=10.56, h=5.64),
            stats=RegionConfig(x=31.02, y=47.58, w=12.13, h=4.22),
            medal=RegionConfig(x=43.71, y=48.20, w=3.86, h=7.45),
            ratio=RegionConfig(x=43.71, y=54.91, w=3.86, h=4.22),
            hero=RegionConfig(x=14.34001273074475, y=47.33, w=4.640203691915978, h=10.584922206506366),
        ),
        # Player 4
        PlayerRegionConfig(
            nickname=RegionConfig(x=21.02, y=59.41, w=10.56, h=5.64),
            stats=RegionConfig(x=30.97, y=60.25, w=12.13, h=4.22),
            medal=RegionConfig(x=43.66, y=61.37, w=3.86, h=7.45),
            ratio=RegionConfig(x=43.77, y=67.95, w=3.86, h=4.22),
            hero=RegionConfig(x=14.33635900700191, y=59.94567185289957, w=4.703857415658817, h=10.867807637906647),
        ),
        # Player 5
        PlayerRegionConfig(
            nickname=RegionConfig(x=20.96, y=72.21, w=10.56, h=5.76),
            stats=RegionConfig(x=31.02, y=73.04, w=12.13, h=4.22),
            medal=RegionConfig(x=43.71, y=73.54, w=3.86, h=7.45),
            ratio=RegionConfig(x=43.71, y=80.62, w=3.86, h=4.22),
            hero=RegionConfig(x=14.34001273074475, y=72.74567185289958, w=4.767511139401655, h=10.867807637906647),
        ),
    ]
)


class ExtractorConfig:
    """
    Gerenciador de configuração do extrator.
    
    Permite carregar, salvar e gerenciar múltiplos perfis de resolução.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o gerenciador de configuração.

        Args:
            config_path: Caminho opcional para arquivo de configuração JSON
        """
        self.profiles: Dict[str, ResolutionProfile] = {
            DEFAULT_PROFILE.name: DEFAULT_PROFILE
        }
        self.active_profile_name: str = DEFAULT_PROFILE.name
        self.tesseract_cmd: Optional[str] = None
        self.output_dir: str = "output"
        self.debug_mode: bool = False
        self.debug_dir: str = "debug"
        
        if config_path:
            self.load_from_file(config_path)

    @property
    def active_profile(self) -> ResolutionProfile:
        """Retorna o perfil de resolução ativo."""
        return self.profiles[self.active_profile_name]

    def set_active_profile(self, profile_name: str) -> None:
        """
        Define o perfil ativo pelo nome.

        Args:
            profile_name: Nome do perfil a ser ativado

        Raises:
            KeyError: Se o perfil não existir
        """
        if profile_name not in self.profiles:
            raise KeyError(f"Perfil '{profile_name}' não encontrado. "
                          f"Disponíveis: {list(self.profiles.keys())}")
        self.active_profile_name = profile_name

    def add_profile(self, profile: ResolutionProfile) -> None:
        """
        Adiciona um novo perfil de resolução.

        Args:
            profile: Perfil de resolução a ser adicionado
        """
        self.profiles[profile.name] = profile

    def remove_profile(self, profile_name: str) -> None:
        """
        Remove um perfil de resolução.

        Args:
            profile_name: Nome do perfil a ser removido

        Raises:
            ValueError: Se tentar remover o perfil padrão ou o perfil ativo
        """
        if profile_name == DEFAULT_PROFILE.name:
            raise ValueError("Não é possível remover o perfil padrão")
        if profile_name == self.active_profile_name:
            raise ValueError("Não é possível remover o perfil ativo")
        del self.profiles[profile_name]

    def list_profiles(self) -> List[str]:
        """Retorna lista de nomes dos perfis disponíveis."""
        return list(self.profiles.keys())

    def load_from_file(self, config_path: str) -> None:
        """
        Carrega configuração de um arquivo JSON.

        Args:
            config_path: Caminho para o arquivo de configuração
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Carregar configurações gerais
        self.tesseract_cmd = data.get("tesseract_cmd")
        self.output_dir = data.get("output_dir", "output")
        self.debug_mode = data.get("debug_mode", False)
        self.debug_dir = data.get("debug_dir", "debug")
        
        # Carregar perfis
        if "profiles" in data:
            for profile_data in data["profiles"]:
                profile = ResolutionProfile.from_dict(profile_data)
                self.profiles[profile.name] = profile
        
        # Definir perfil ativo
        if "active_profile" in data and data["active_profile"] in self.profiles:
            self.active_profile_name = data["active_profile"]

    def save_to_file(self, config_path: str) -> None:
        """
        Salva configuração em um arquivo JSON.

        Args:
            config_path: Caminho para salvar o arquivo de configuração
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "tesseract_cmd": self.tesseract_cmd,
            "output_dir": self.output_dir,
            "debug_mode": self.debug_mode,
            "debug_dir": self.debug_dir,
            "active_profile": self.active_profile_name,
            "profiles": [p.to_dict() for p in self.profiles.values()],
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_sample_config(self, output_path: str = "resolutions/default.json") -> str:
        """
        Cria um arquivo de configuração de exemplo.

        Args:
            output_path: Caminho para o arquivo de exemplo

        Returns:
            Caminho do arquivo criado
        """
        self.save_to_file(output_path)
        return output_path

    def auto_select_profile(self, image_width: int, image_height: int) -> str:
        """
        Seleciona automaticamente o perfil mais adequado para a resolução da imagem.
        
        Compara a proporção (aspect ratio) da imagem com os perfis disponíveis
        e seleciona o mais próximo.

        Args:
            image_width: Largura da imagem em pixels
            image_height: Altura da imagem em pixels

        Returns:
            Nome do perfil selecionado
        """
        image_ratio = image_width / image_height
        best_profile = DEFAULT_PROFILE.name
        best_diff = float('inf')
        
        for name, profile in self.profiles.items():
            profile_ratio = profile.reference_width / profile.reference_height
            diff = abs(image_ratio - profile_ratio)
            if diff < best_diff:
                best_diff = diff
                best_profile = name
        
        self.active_profile_name = best_profile
        return best_profile
