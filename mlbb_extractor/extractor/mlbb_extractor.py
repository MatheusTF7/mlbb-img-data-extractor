"""
MLBB Player Data Extractor.

Este módulo é responsável pela extração de dados de jogadores a partir de
screenshots de final de partida do Mobile Legends Bang Bang.

Funcionalidades:
- Busca de jogador específico por nickname
- Extração de dados de todos os jogadores do time aliado
- Extração de informações da partida (resultado, placar, duração)
- Suporte a múltiplos perfis de resolução
"""

import re
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from ..preprocessor.image_processor import ImagePreprocessor
from ..config import (
    ExtractorConfig, RegionConfig, PlayerRegionConfig, 
    ResolutionProfile, DEFAULT_PROFILE
)


class MedalType(Enum):
    """Tipos de medalha baseados em cor."""
    GOLD = "GOLD"
    SILVER = "SILVER"
    BRONZE = "BRONZE"
    NONE = "NONE"


@dataclass
class PlayerStats:
    """Dados estatísticos de um jogador."""
    nickname: str
    kills: int
    deaths: int
    assists: int
    gold: int
    medal: str
    ratio: float
    position: int  # Posição 1-5 no time


@dataclass
class MatchInfo:
    """Informações da partida."""
    result: str  # VICTORY ou DEFEAT
    my_team_score: int
    adversary_team_score: int
    duration: str  # Formato mm:ss


@dataclass
class GameData:
    """Dados completos do jogo para um jogador específico."""
    nickname: str
    kills: int
    deaths: int
    assists: int
    gold: int
    medal: str
    ratio: float
    result: str
    my_team_score: int
    adversary_team_score: int
    duration: str

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "nickname": self.nickname,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "gold": self.gold,
            "medal": self.medal,
            "ratio": self.ratio,
            "result": self.result,
            "my_team_score": self.my_team_score,
            "adversary_team_score": self.adversary_team_score,
            "duration": self.duration,
        }


class MLBBExtractor:
    """
    Extrai dados de jogadores de screenshots do MLBB.
    
    Esta classe fornece métodos para:
    - Encontrar um jogador específico pelo nickname
    - Extrair estatísticas (K/D/A, ouro, medalha, rating)
    - Extrair informações da partida (resultado, placar, duração)
    
    Attributes:
        config: Configuração com perfis de resolução
        preprocessor: Processador de imagem para pré-processamento OCR
        pytesseract: Módulo pytesseract para OCR
    """

    def __init__(
        self, 
        tesseract_cmd: Optional[str] = None,
        config: Optional[ExtractorConfig] = None
    ):
        """
        Inicializa o extrator MLBB.

        Args:
            tesseract_cmd: Caminho opcional para o executável do Tesseract
            config: Configuração opcional com perfis de resolução
        """
        self.config = config or ExtractorConfig()
        if tesseract_cmd:
            self.config.tesseract_cmd = tesseract_cmd
        
        self.preprocessor = ImagePreprocessor()
        
        # Configurar pytesseract
        import pytesseract
        if self.config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd
        self.pytesseract = pytesseract

    @property
    def profile(self) -> ResolutionProfile:
        """Retorna o perfil de resolução ativo."""
        return self.config.active_profile

    def _extract_region(
        self, 
        image: np.ndarray, 
        region: RegionConfig
    ) -> np.ndarray:
        """Extrai uma região da imagem usando coordenadas percentuais."""
        height, width = image.shape[:2]
        x, y, w, h = region.to_pixels(width, height)
        return image[y:y+h, x:x+w]

    # =========================================================================
    # EXTRAÇÃO DE INFORMAÇÕES DA PARTIDA
    # =========================================================================

    def extract_match_info(self, image: np.ndarray) -> MatchInfo:
        """
        Extrai informações da partida (resultado, placar, duração).
        
        Args:
            image: Imagem completa do screenshot
            
        Returns:
            MatchInfo com dados da partida
        """
        profile = self.profile
        
        # Extrair resultado (VICTORY/DEFEAT)
        result_region = self._extract_region(image, profile.result_region)
        processed = self.preprocessor.preprocess_threshold(result_region, 4)
        result_text = self.pytesseract.image_to_string(
            processed, 
            config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ).strip()
        result = self._parse_result(result_text)
        
        # Extrair placar do meu time
        my_score_region = self._extract_region(image, profile.my_team_score_region)
        processed = self.preprocessor.preprocess_grayscale_scaled(my_score_region, 3)
        my_score_text = self.pytesseract.image_to_string(
            processed, config="--psm 7 -c tessedit_char_whitelist=0123456789"
        ).strip()
        my_score = self._parse_number(my_score_text, 0)
        
        # Extrair placar adversário
        adv_score_region = self._extract_region(image, profile.adversary_score_region)
        processed = self.preprocessor.preprocess_grayscale_scaled(adv_score_region, 3)
        adv_score_text = self.pytesseract.image_to_string(
            processed, config="--psm 7 -c tessedit_char_whitelist=0123456789"
        ).strip()
        adv_score = self._parse_number(adv_score_text, 0)
        
        # Extrair duração
        duration_region = self._extract_region(image, profile.duration_region)
        processed = self.preprocessor.preprocess_grayscale_scaled(duration_region, 2)
        duration_text = self.pytesseract.image_to_string(
            processed, config="--psm 7 -c tessedit_char_whitelist=0123456789:"
        ).strip()
        duration = self._parse_duration(duration_text)
        
        return MatchInfo(
            result=result,
            my_team_score=my_score,
            adversary_team_score=adv_score,
            duration=duration
        )

    # =========================================================================
    # EXTRAÇÃO DE DADOS DO JOGADOR
    # =========================================================================

    def extract_player_nickname(
        self, 
        image: np.ndarray, 
        player_config: PlayerRegionConfig
    ) -> str:
        """Extrai o nickname de um jogador."""
        nickname_region = self._extract_region(image, player_config.nickname)
        processed = self.preprocessor.preprocess_grayscale_scaled(nickname_region, 2)
        nickname = self.pytesseract.image_to_string(processed, config="--psm 7").strip()
        return self._clean_nickname(nickname)

    def extract_player_stats(
        self, 
        image: np.ndarray, 
        player_config: PlayerRegionConfig
    ) -> Tuple[int, int, int, int]:
        """
        Extrai kills, deaths, assists e ouro da região de stats do jogador.
        
        Utiliza múltiplas estratégias para extrair os 4 valores.
        
        Returns:
            Tupla (kills, deaths, assists, gold)
        """
        stats_region = self._extract_region(image, player_config.stats)
        
        # Estratégia 1: PSM 6 (bloco uniforme) que às vezes preserva espaços
        processed = self.preprocessor.preprocess_grayscale_scaled(stats_region, 3)
        text1 = self.pytesseract.image_to_string(
            processed, 
            config="--psm 6 -c tessedit_char_whitelist=0123456789 "
        ).strip()
        
        numbers = re.findall(r'\d+', text1)
        if len(numbers) >= 4:
            return (int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
        
        # Estratégia 2: Tentar com pré-processamento diferente (invertido)
        inverted = self.preprocessor.preprocess_inverted(stats_region, 3)
        text2 = self.pytesseract.image_to_string(
            inverted, 
            config="--psm 6 -c tessedit_char_whitelist=0123456789 "
        ).strip()
        
        numbers = re.findall(r'\d+', text2)
        if len(numbers) >= 4:
            return (int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
        
        # Estratégia 3: Usar image_to_data para obter bounding boxes das palavras
        data = self.pytesseract.image_to_data(processed, output_type=self.pytesseract.Output.DICT)
        words = [w for w in data['text'] if w.strip()]
        word_numbers = []
        for w in words:
            digits = ''.join(filter(str.isdigit, w))
            if digits:
                word_numbers.append(int(digits))
        
        if len(word_numbers) >= 4:
            return (word_numbers[0], word_numbers[1], word_numbers[2], word_numbers[3])
        
        # Estratégia 4: Parse inteligente de string concatenada
        best_text = text1 if text1 else text2
        all_digits = ''.join(filter(str.isdigit, best_text))
        
        if len(all_digits) >= 7:
            return self._parse_concatenated_stats_smart(all_digits)
        
        # Estratégia 5: Se temos 3 word_numbers, tentar dividir o primeiro
        # Ex: ['2410', '6', '28311'] -> tentar dividir '2410' em kills e deaths
        if len(word_numbers) == 3:
            first = str(word_numbers[0])
            if len(first) >= 2:
                for split_at in [1, 2]:
                    if split_at < len(first):
                        k = int(first[:split_at])
                        d = int(first[split_at:])
                        a = word_numbers[1]
                        gold = word_numbers[2]
                        
                        if 0 <= k <= 50 and 0 <= d <= 30 and 0 <= a <= 50 and gold >= 1000:
                            return (k, d, a, gold)
        
        return (0, 0, 0, 0)

    def _parse_concatenated_stats_smart(self, digits: str) -> Tuple[int, int, int, int]:
        """
        Parse inteligente de stats concatenados sabendo que ouro tem 4-5 dígitos.
        
        Formato: K D A Gold onde:
        - K, D, A são 1-2 dígitos cada
        - Gold é 4-5 dígitos (tipicamente 5000-30000)
        """
        if len(digits) < 7:
            return (0, 0, 0, 0)
        
        best_result = (0, 0, 0, 0)
        best_score = -1
        
        for gold_len in [5, 4]:
            if len(digits) < gold_len + 3:
                continue
            
            gold_str = digits[-gold_len:]
            kda_str = digits[:-gold_len]
            
            gold = int(gold_str)
            
            if not (3000 <= gold <= 40000):
                continue
            
            kda = self._parse_kda_all_combinations(kda_str)
            
            if kda:
                score = 10 if (8000 <= gold <= 30000) else 5
                
                if score > best_score:
                    best_score = score
                    best_result = (kda[0], kda[1], kda[2], gold)
        
        return best_result

    def _parse_kda_all_combinations(self, kda_str: str) -> Optional[Tuple[int, int, int]]:
        """Tenta todas as combinações válidas de K/D/A e retorna a mais razoável."""
        length = len(kda_str)
        
        if length < 3:
            return None
        
        valid_parses = []
        
        for k_len in range(1, min(3, length-1)):
            for d_len in range(1, min(3, length-k_len)):
                a_len = length - k_len - d_len
                if not (1 <= a_len <= 3):
                    continue
                
                try:
                    k = int(kda_str[:k_len])
                    d = int(kda_str[k_len:k_len+d_len])
                    a = int(kda_str[k_len+d_len:])
                    
                    if 0 <= k <= 50 and 0 <= d <= 30 and 0 <= a <= 50:
                        score = 0
                        
                        if d < k + a:
                            score += 10
                        
                        if k > 0 and a > 0:
                            ratio = max(k, a) / min(k, a)
                            if ratio < 10:
                                score += 5
                            if ratio < 5:
                                score += 3
                        
                        digit_variance = abs(k_len - d_len) + abs(d_len - a_len)
                        score += max(0, 5 - digit_variance * 2)
                        
                        if length == 6 and k_len == d_len == a_len == 2:
                            score += 5
                        
                        if length == 5 and k_len == 2 and d_len == 2 and a_len == 1:
                            score += 5
                        
                        if d_len == 1 and d <= 1 and (k >= 10 or a >= 10):
                            score -= 5
                        
                        if 5 <= d <= 15:
                            score += 3
                        
                        valid_parses.append((score, k, d, a))
                except ValueError:
                    continue
        
        if valid_parses:
            valid_parses.sort(reverse=True)
            _, k, d, a = valid_parses[0]
            return (k, d, a)
        
        return None

    def extract_player_ratio(
        self, 
        image: np.ndarray, 
        player_config: PlayerRegionConfig
    ) -> float:
        """Extrai o rating de performance do jogador."""
        ratio_region = self._extract_region(image, player_config.ratio)
        
        processed = self.preprocessor.preprocess_grayscale_scaled(ratio_region, 6)
        tesseract_config = "--psm 8 -c tessedit_char_whitelist=0123456789."
        ratio_text = self.pytesseract.image_to_string(processed, config=tesseract_config).strip()
        
        result = self._parse_float(ratio_text, 0.0)
        
        if result > 0:
            return result
        
        # Fallback: tentar máscara de cor amarela para badges dourados
        yellow_mask = self.preprocessor.preprocess_yellow_color_mask(ratio_region, 5)
        ratio_text = self.pytesseract.image_to_string(yellow_mask, config=tesseract_config).strip()
        
        return self._parse_float(ratio_text, 0.0)

    def extract_player_medal(
        self, 
        image: np.ndarray, 
        player_config: PlayerRegionConfig
    ) -> str:
        """
        Detecta a cor da medalha (GOLD, SILVER, BRONZE) do jogador.
        Usa análise de cor ao invés de OCR.
        """
        medal_region = self._extract_region(image, player_config.medal)
        return self._detect_medal_color(medal_region)

    def _detect_medal_color(self, region: np.ndarray) -> str:
        """Detecta tipo de medalha baseado na cor dominante."""
        if region.size == 0:
            return MedalType.NONE.value
        
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        
        # Ranges de cor
        gold_lower = np.array([15, 80, 120])
        gold_upper = np.array([35, 255, 255])
        
        silver_lower = np.array([0, 0, 150])
        silver_upper = np.array([180, 50, 255])
        
        bronze_lower = np.array([8, 80, 80])
        bronze_upper = np.array([20, 255, 200])
        
        gold_mask = cv2.inRange(hsv, gold_lower, gold_upper)
        silver_mask = cv2.inRange(hsv, silver_lower, silver_upper)
        bronze_mask = cv2.inRange(hsv, bronze_lower, bronze_upper)
        
        gold_pixels = cv2.countNonZero(gold_mask)
        silver_pixels = cv2.countNonZero(silver_mask)
        bronze_pixels = cv2.countNonZero(bronze_mask)
        
        max_pixels = max(gold_pixels, silver_pixels, bronze_pixels)
        
        if max_pixels < 50:
            return MedalType.NONE.value
        
        if max_pixels == gold_pixels:
            return MedalType.GOLD.value
        elif max_pixels == silver_pixels:
            return MedalType.SILVER.value
        else:
            return MedalType.BRONZE.value

    # =========================================================================
    # BUSCA DE JOGADOR
    # =========================================================================

    def find_player_by_nickname(
        self, 
        image: np.ndarray, 
        target_nickname: str
    ) -> Optional[int]:
        """
        Encontra a posição de um jogador pelo nickname.
        
        Busca o nickname em todas as 5 posições do time aliado e retorna
        a posição quando encontrado.
        
        Args:
            image: Imagem completa do screenshot
            target_nickname: Nickname a ser buscado
            
        Returns:
            Posição do jogador (0-4) ou None se não encontrado
        """
        target_lower = target_nickname.lower().strip()
        
        for idx, player_config in enumerate(self.profile.players):
            nickname = self.extract_player_nickname(image, player_config)
            nickname_lower = nickname.lower().strip()
            
            # Match exato ou parcial
            if target_lower in nickname_lower or nickname_lower in target_lower:
                return idx
            
            # Match por similaridade
            if self._similar_names(target_lower, nickname_lower):
                return idx
        
        return None

    def _similar_names(self, name1: str, name2: str, threshold: float = 0.6) -> bool:
        """Verifica se dois nomes são similares usando ratio de caracteres."""
        if not name1 or not name2:
            return False
        
        set1, set2 = set(name1), set(name2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return False
        
        return (intersection / union) >= threshold

    # =========================================================================
    # MÉTODOS DE EXTRAÇÃO COMPLETA
    # =========================================================================

    def extract_player_data(
        self, 
        image: np.ndarray, 
        player_index: int
    ) -> PlayerStats:
        """
        Extrai todos os dados de um jogador por posição.
        
        Args:
            image: Imagem completa do screenshot
            player_index: Posição do jogador (0-4)
            
        Returns:
            PlayerStats com todos os dados do jogador
        """
        player_config = self.profile.players[player_index]
        
        nickname = self.extract_player_nickname(image, player_config)
        kills, deaths, assists, gold = self.extract_player_stats(image, player_config)
        ratio = self.extract_player_ratio(image, player_config)
        medal = self.extract_player_medal(image, player_config)
        
        return PlayerStats(
            nickname=nickname,
            kills=kills,
            deaths=deaths,
            assists=assists,
            gold=gold,
            medal=medal,
            ratio=ratio,
            position=player_index + 1
        )

    def extract_game_data(
        self, 
        image_path: str, 
        player_nickname: str
    ) -> Optional[GameData]:
        """
        Extrai dados completos do jogo para um jogador específico.
        
        Este é o método principal para buscar um jogador específico pelo nickname
        e extrair todos os seus dados da partida.
        
        Args:
            image_path: Caminho para a imagem do screenshot
            player_nickname: Nickname do jogador a ser buscado
            
        Returns:
            GameData com todos os dados ou None se jogador não encontrado
        """
        # Carregar imagem
        image = self.preprocessor.load_image(image_path)
        
        # Auto-selecionar perfil baseado na resolução da imagem
        height, width = image.shape[:2]
        self.config.auto_select_profile(width, height)
        
        # Encontrar posição do jogador
        player_index = self.find_player_by_nickname(image, player_nickname)
        
        if player_index is None:
            print(f"Jogador '{player_nickname}' não encontrado no screenshot")
            return None
        
        # Extrair informações da partida
        match_info = self.extract_match_info(image)
        
        # Extrair dados do jogador
        player_stats = self.extract_player_data(image, player_index)
        
        return GameData(
            nickname=player_stats.nickname,
            kills=player_stats.kills,
            deaths=player_stats.deaths,
            assists=player_stats.assists,
            gold=player_stats.gold,
            medal=player_stats.medal,
            ratio=player_stats.ratio,
            result=match_info.result,
            my_team_score=match_info.my_team_score,
            adversary_team_score=match_info.adversary_team_score,
            duration=match_info.duration
        )

    def extract_all_players(
        self, 
        image_path: str
    ) -> List[Dict[str, Any]]:
        """
        Extrai dados de todos os 5 jogadores do time aliado.
        
        Args:
            image_path: Caminho para a imagem do screenshot
            
        Returns:
            Lista de dicionários com dados de cada jogador
        """
        image = self.preprocessor.load_image(image_path)
        
        # Auto-selecionar perfil
        height, width = image.shape[:2]
        self.config.auto_select_profile(width, height)
        
        match_info = self.extract_match_info(image)
        
        results = []
        for idx in range(5):
            player_stats = self.extract_player_data(image, idx)
            data = {
                "nickname": player_stats.nickname,
                "kills": player_stats.kills,
                "deaths": player_stats.deaths,
                "assists": player_stats.assists,
                "gold": player_stats.gold,
                "medal": player_stats.medal,
                "ratio": player_stats.ratio,
                "position": player_stats.position,
                "result": match_info.result,
                "my_team_score": match_info.my_team_score,
                "adversary_team_score": match_info.adversary_team_score,
                "duration": match_info.duration
            }
            results.append(data)
        
        return results

    # =========================================================================
    # MÉTODOS AUXILIARES DE PARSING
    # =========================================================================

    def _parse_result(self, text: str) -> str:
        """Parse resultado do jogo a partir de texto."""
        text_upper = text.upper()
        if "VICTORY" in text_upper or "VICTOR" in text_upper or "WIN" in text_upper:
            return "VICTORY"
        elif "DEFEAT" in text_upper or "LOSE" in text_upper or "LOSS" in text_upper:
            return "DEFEAT"
        return "UNKNOWN"

    def _parse_number(self, text: str, default: int = 0) -> int:
        """Parse inteiro de texto."""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return default

    def _parse_float(self, text: str, default: float = 0.0) -> float:
        """Parse float de texto."""
        match = re.search(r'(\d+\.?\d*|\.\d+)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return default

    def _parse_duration(self, text: str) -> str:
        """Parse duração no formato mm:ss."""
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 2:
            return f"{numbers[0]}:{numbers[1].zfill(2)}"
        
        return "00:00"

    def _clean_nickname(self, text: str) -> str:
        """Limpa nickname extraído."""
        cleaned = text.strip()
        cleaned = re.sub(r'^[@#$%^&*()_+=\[\]{}|\\<>/?`~]+', '', cleaned)
        cleaned = re.sub(r'[@#$%^&*()_+=\[\]{}|\\<>/?`~]+$', '', cleaned)
        cleaned = cleaned.replace('\n', '').replace('\r', '')
        return cleaned.strip()
