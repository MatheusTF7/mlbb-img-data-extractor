# MLBB Image Data Extractor

Extrai dados de jogadores de screenshots de final de partida do **Mobile Legends Bang Bang** usando OCR (Tesseract) e processamento de imagem (OpenCV).

## Funcionalidades

- 🔍 **Busca por jogador**: Encontra um jogador específico pelo nickname
- 📊 **Extração completa**: Extrai K/D/A, ouro, medalha e rating
- 👥 **Todos os jogadores**: Extrai dados dos 5 jogadores do time aliado
- 🎯 **Multi-resolução**: Suporte a múltiplos perfis de resolução via configuração
- 📄 **Exportação JSON**: Exporta dados estruturados em formato JSON
- 🐛 **Modo Debug**: Salva imagens intermediárias para diagnóstico e ajustes

## Requisitos

- Python 3.10+
- Tesseract OCR instalado
- OpenCV
- pytesseract

## Instalação

### 1. Instalar Tesseract OCR

**Windows:**
- Baixe o instalador de: https://github.com/UB-Mannheim/tesseract/wiki
- Instale em `C:\Program Files\Tesseract-OCR\`

**Linux:**
```bash
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Instalar dependências Python

```bash
pip install -r requirements.txt
```

Ou instalar o pacote:

```bash
pip install -e .
```

## Uso

### Interface de Linha de Comando

#### Buscar um jogador específico

```bash
python main.py -i screenshot.png -p "NicknameJogador"
```

#### Extrair todos os jogadores

```bash
python main.py -i screenshot.png --all-players
```

#### Especificar caminho do Tesseract

Se o Tesseract não estiver no PATH:

```bash
python main.py -i screenshot.png -p "MTF7" --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

#### Gerar arquivo de configuração

```bash
python main.py --generate-config
```

Isto criará `resolutions/default.json` com o perfil padrão.

#### Listar perfis de resolução

```bash
python main.py --list-profiles
```

#### Modo Debug

Ativa o modo debug para salvar todas as imagens intermediárias na pasta `debug/`:

```bash
# Com debug ativado
python main.py -i screenshot.png --all-players --debug

# Processar múltiplas imagens com debug
python main.py -d ./screenshots --all-players --debug
```

📖 **Para mais informações sobre o modo debug, consulte:** [DEBUG_MODE.md](DEBUG_MODE.md)

### Uso como Biblioteca

```python
from mlbb_extractor import MLBBExtractor

# Criar extrator
extractor = MLBBExtractor(tesseract_cmd="C:/Program Files/Tesseract-OCR/tesseract.exe")

# Buscar dados de um jogador específico
game_data = extractor.extract_game_data("screenshot.png", "MTF7")

if game_data:
    print(f"Jogador: {game_data.nickname}")
    print(f"K/D/A: {game_data.kills}/{game_data.deaths}/{game_data.assists}")
    print(f"Ouro: {game_data.gold}")
    print(f"Rating: {game_data.ratio}")
    print(f"Medalha: {game_data.medal}")
    print(f"Resultado: {game_data.result}")

# Extrair todos os jogadores
all_players = extractor.extract_all_players("screenshot.png")

for player in all_players:
    print(f"{player['position']}. {player['nickname']}: {player['kills']}/{player['deaths']}/{player['assists']}")
```

### Usando Arquivo de Configuração

```python
from mlbb_extractor import MLBBExtractor, ExtractorConfig

# Carregar configuração de arquivo
config = ExtractorConfig("resolutions/default.json")

# Criar extrator com configuração
extractor = MLBBExtractor(config=config)

# Usar perfil específico
extractor.config.set_active_profile("default_2400x1080")
```

## Configuração

Os arquivos de configuração ficam na pasta `resolutions/` e permitem definir múltiplos perfis de resolução.

Gere o arquivo padrão com:

```bash
python main.py --generate-config
```

Isto criará `resolutions/default.json`:

```json
{
  "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
  "output_dir": "output",
  "active_profile": "default_2400x1080",
  "profiles": [
    {
      "name": "default_2400x1080",
      "description": "Perfil padrão para resolução 2400x1080",
      "reference_width": 2400,
      "reference_height": 1080,
      "result_region": {"x": 40.02, "y": 3.11, "w": 19.90, "h": 10.68},
      "my_team_score_region": {"x": 32.48, "y": 5.09, "w": 4.97, "h": 8.57},
      "adversary_score_region": {"x": 62.60, "y": 5.22, "w": 4.81, "h": 7.95},
      "duration_region": {"x": 77.25, "y": 11.43, "w": 4.58, "h": 4.10},
      "players": [
        {
          "nickname": {"x": 21.07, "y": 22.11, "w": 10.56, "h": 4.22},
          "stats": {"x": 31.13, "y": 21.99, "w": 12.13, "h": 4.22},
          "medal": {"x": 43.77, "y": 22.61, "w": 3.86, "h": 7.45},
          "ratio": {"x": 43.77, "y": 29.32, "w": 3.86, "h": 4.22}
        }
      ]
    }
  ]
}
```

### Coordenadas em Porcentagem

Todas as coordenadas são definidas em **porcentagem** (0-100) da imagem, o que permite que as regiões funcionem em imagens de diferentes resoluções mantendo a mesma proporção.

- `x`: Posição horizontal em porcentagem
- `y`: Posição vertical em porcentagem  
- `w`: Largura em porcentagem
- `h`: Altura em porcentagem

## Estrutura do Projeto

```
mlbb-img-data-extractor/
├── main.py                      # CLI principal
├── resolutions/                 # Arquivos de configuração
│   └── default.json           # Perfil padrão 2400x1080
├── requirements.txt             # Dependências Python
├── setup.py                     # Instalação do pacote
├── DEBUG_MODE.md                # Documentação do modo debug
├── test_debug.py                # Script de teste do modo debug
├── mlbb_extractor/
│   ├── __init__.py             # Exports do pacote
│   ├── config.py               # Sistema de configuração multi-resolução
│   ├── extractor/
│   │   ├── __init__.py
│   │   └── mlbb_extractor.py   # Extrator principal
│   └── preprocessor/
│       ├── __init__.py
│       └── image_processor.py  # Pré-processamento de imagem
├── images/                      # Screenshots de teste
├── output/                      # Arquivos exportados
└── debug/                       # Imagens de debug (quando ativado)
```

## Dados Extraídos

### Por Jogador

| Campo | Descrição |
|-------|-----------|
| `nickname` | Nome do jogador |
| `kills` | Número de abates |
| `deaths` | Número de mortes |
| `assists` | Número de assistências |
| `gold` | Ouro total obtido |
| `medal` | Tipo de medalha (GOLD, SILVER, BRONZE) |
| `ratio` | Rating de performance |
| `position` | Posição no time (1-5) |

### Informações da Partida

| Campo | Descrição |
|-------|-----------|
| `result` | Resultado (VICTORY/DEFEAT) |
| `my_team_score` | Placar do time aliado |
| `adversary_team_score` | Placar do time adversário |
| `duration` | Duração da partida (mm:ss) |

## Exemplo de Saída

```json
{
  "nickname": "MTF7",
  "kills": 10,
  "deaths": 9,
  "assists": 14,
  "gold": 12906,
  "medal": "GOLD",
  "ratio": 9.47,
  "result": "DEFEAT",
  "my_team_score": 36,
  "adversary_team_score": 41,
  "duration": "30:50"
}
```

## Adicionando Novos Perfis de Resolução

Se seus screenshots têm proporções diferentes do perfil padrão (2400x1080):

1. Gere o arquivo de configuração:
   ```bash
   python main.py --generate-config
   ```

2. Copie `resolutions/default.json` para um novo arquivo:
   ```bash
   cp resolutions/default.json resolutions/1920x1080.json
   ```

3. Edite o novo arquivo e ajuste as coordenadas

4. Use o perfil:
   ```bash
   python main.py -i screenshot.png --all-players --config resolutions/1920x1080.json
   ```

## Troubleshooting

### OCR não funciona

1. Verifique se o Tesseract está instalado corretamente
2. Use `--tesseract-cmd` para especificar o caminho completo
3. Verifique se a imagem está em boa qualidade

### Jogador não encontrado

1. Verifique se o nickname está correto (case-sensitive)
2. **Use o modo debug** (`--debug`) para visualizar as extrações
3. Verifique se a resolução da imagem é compatível com o perfil usado
4. Ajuste as coordenadas do perfil se necessário

### Coordenadas incorretas

1. **Ative o modo debug** com `--debug`
2. Examine os arquivos `*_raw.png` na pasta `debug/`
3. Ajuste as coordenadas percentuais no arquivo de configuração
4. Teste novamente até os cortes estarem corretos

### Dados extraídos incorretamente

1. **Use o modo debug** para ver as imagens processadas
2. Examine os arquivos `*_processed.png` na pasta `debug/`
3. Se o texto não estiver legível, considere ajustar os parâmetros de pré-processamento
4. Veja [DEBUG_MODE.md](DEBUG_MODE.md) para mais detalhes

1. O nickname pode ter caracteres especiais que o OCR não reconhece
2. Use parte do nickname (busca parcial é suportada)
3. Verifique se o jogador está no time da esquerda (aliado)

### Valores incorretos

1. A resolução da imagem pode ser diferente do perfil ativo
2. Crie um perfil customizado com coordenadas ajustadas
3. Use `--list-profiles` para ver os perfis disponíveis

## Licença

MIT License
