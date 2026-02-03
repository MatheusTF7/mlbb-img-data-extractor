# Atualização: Suporte para Extração de Heróis

## Resumo das Mudanças

O projeto foi atualizado para suportar a identificação automática dos heróis utilizados pelos jogadores através de **Feature Matching (ORB) combinado com Histograma de Cores**.

## Algoritmo de Identificação

O sistema utiliza uma **abordagem híbrida** para identificar heróis:

### 1. ORB Feature Matching
- **ORB (Oriented FAST and Rotated BRIEF)** detecta características visuais distintas
- Compara keypoints entre a região extraída e as imagens de referência
- Usa **Lowe's Ratio Test** para filtrar bons matches
- Ideal quando há features distintas na imagem

### 2. Histograma de Cores (HSV)
- Compara distribuição de cores usando espaço HSV (mais robusto a variações de luz)
- Usa correlação para calcular similaridade
- **Fallback** quando ORB não encontra features suficientes

### 3. Score Combinado
- Se ORB encontra bons matches: **60% ORB + 40% Histograma**
- Se ORB falha: **20% ORB + 80% Histograma**
- Threshold de confiança: **20%** (ajustável)

## Arquivos Modificados

### 1. `mlbb_extractor/config.py`
- **PlayerRegionConfig**: Adicionado campo opcional `hero: Optional[RegionConfig]`
- **DEFAULT_PROFILE**: Atualizado com coordenadas da área `hero` para os 5 jogadores

### 2. `mlbb_extractor/extractor/mlbb_extractor.py`

#### Estruturas de Dados
- **PlayerStats**: Campo `hero: str = ""`
- **GameData**: Campo `hero: str = ""` incluído no `to_dict()`

#### Inicialização
- `_load_heroes_map()`: Carrega `heroes_map.json`
- `_load_hero_images()`: Carrega imagens e **pré-computa descriptors ORB**

#### Método Principal
- **`extract_player_hero()`**: Implementa o algoritmo híbrido
  - Extrai região do herói do screenshot
  - Detecta features ORB na região
  - Calcula histograma de cores HSV
  - Combina scores de ambos os métodos
  - Retorna nome do herói ou `"NO_MATCH"`

### 3. `main.py`
- Exibe o herói identificado no output do console

## Uso

```bash
# Comando básico
python main.py -i ./images/screenshot.png --all-players --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Com debug (mostra scores de matching)
python main.py -i ./images/screenshot.png --all-players --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe" --debug
```

## Output de Exemplo

```
Jogador 1: ATF7-
  Herói: Minotauro
  K/D/A: 0/8/16
  Ouro: 11301
  Rating: 7.6
  Medalha: GOLD
  MVP: -

Jogador 2: nny-
  Herói: NO_MATCH
  K/D/A: 3/6/11
  ...
```

## JSON de Saída

```json
{
  "my_team": [
    {
      "nickname": "ATF7",
      "hero": "Minotauro",
      "kills": 0,
      "deaths": 8,
      "assists": 16,
      ...
    }
  ]
}
```

## Adicionando Novos Heróis

1. Adicione a imagem do herói em `/image_heroes/nome_heroi.png`
2. Atualize `heroes_map.json`:
```json
{
  "mappings": {
    "NovoHeroi": "/image_heroes/novo_heroi.png"
  }
}
```

## Dependências

Nenhuma nova dependência. Usa:
- `opencv-python` (cv2) - ORB, histogramas
- `numpy` - manipulação de arrays

## Compatibilidade

- ✅ Retrocompatível: sem `hero` configurado → retorna `"NO_MATCH"`
- ✅ Sem `heroes_map.json` → extração continua normalmente
