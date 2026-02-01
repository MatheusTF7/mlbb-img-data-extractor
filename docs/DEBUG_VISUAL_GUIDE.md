# Exemplo Visual do Modo Debug

Este documento mostra visualmente o que o modo debug gera e como isso ajuda no diagnóstico.

## Fluxo de Processamento

Quando o modo debug está ativado, cada etapa de extração gera arquivos de imagem:

```
Screenshot Original
       ↓
   [Corte da Região]  ← Salva: *_raw.png
       ↓
  [Pré-processamento] ← Salva: *_processed.png
       ↓
      [OCR]
       ↓
    [Resultado]
```

## Exemplo de Arquivos por Região

### 1. VICTORY/DEFEAT

```
20260201_143052_001_screenshot1_result_raw.png
├─ Imagem: Corte da região onde aparece "VICTORY" ou "DEFEAT"
└─ Tamanho típico: ~200x100 pixels

20260201_143052_002_screenshot1_result_processed.png
├─ Imagem: Após threshold binário (preto e branco)
└─ Melhor para OCR reconhecer letras
```

**Uso**: Se o resultado estiver errado, verifique se:
- O corte contém o texto completo (arquivo `_raw.png`)
- O texto está legível após processamento (arquivo `_processed.png`)

### 2. Placar (Scores)

```
20260201_143052_003_screenshot1_my_team_score_raw.png
20260201_143052_004_screenshot1_my_team_score_processed.png
20260201_143052_005_screenshot1_adversary_score_raw.png
20260201_143052_006_screenshot1_adversary_score_processed.png
```

**Uso**: Verifique se os números estão centrados no corte e legíveis.

### 3. Duração da Partida

```
20260201_143052_007_screenshot1_duration_raw.png
20260201_143052_008_screenshot1_duration_processed.png
```

**Uso**: O formato deve ser "MM:SS". Verifique se ambos os números estão visíveis.

### 4. Dados do Jogador

Para cada jogador processado (1 a 5), são gerados:

#### Nickname
```
20260201_143052_009_screenshot1_nickname_raw.png
20260201_143052_010_screenshot1_nickname_processed.png
```

#### Stats (K/D/A + Gold)
```
20260201_143052_011_screenshot1_stats_raw.png
20260201_143052_012_screenshot1_stats_processed_gray.png      ← Escala de cinza
20260201_143052_013_screenshot1_stats_processed_inverted.png  ← Cores invertidas
```

**Nota**: A extração de stats usa múltiplas estratégias de processamento para aumentar a taxa de sucesso.

#### Ratio/Rating
```
20260201_143052_014_screenshot1_ratio_raw.png
20260201_143052_015_screenshot1_ratio_processed.png
20260201_143052_016_screenshot1_ratio_yellow_mask.png  ← Para medalhas douradas
```

#### Medalha
```
20260201_143052_017_screenshot1_medal_raw.png
```

**Nota**: A medalha é detectada por cor (HSV), não por OCR, então apenas a imagem raw é salva.

## Casos de Uso Práticos

### Caso 1: Nickname Incorreto

**Problema**: O extrator retorna nickname errado, como "MTF?" ao invés de "MTF7"

**Diagnóstico com Debug**:
1. Abra `*_nickname_raw.png` - Verifique se o "7" está no corte
2. Abra `*_nickname_processed.png` - Verifique se o "7" está legível
3. Se o "7" está cortado: Ajuste `w` (largura) na configuração
4. Se está muito escuro/claro: Ajuste parâmetros de pré-processamento

### Caso 2: K/D/A Extraído Incorretamente

**Problema**: Stats retornam como `0/0/0/0` ou valores errados

**Diagnóstico com Debug**:
1. Abra `*_stats_raw.png` - Todos os 4 números estão visíveis?
2. Abra `*_stats_processed_gray.png` - Os números estão legíveis?
3. Abra `*_stats_processed_inverted.png` - Qual processamento ficou melhor?
4. Ajuste coordenadas ou método de processamento conforme necessário

### Caso 3: Resultado UNKNOWN

**Problema**: O resultado da partida não é detectado (retorna "UNKNOWN")

**Diagnóstico com Debug**:
1. Abra `*_result_raw.png` - "VICTORY" ou "DEFEAT" está visível?
2. Abra `*_result_processed.png` - Texto está em alto contraste?
3. Se estiver cortado ou parcial: Ajuste as coordenadas da região
4. Se estiver borrado: Pode ser problema de qualidade da imagem original

## Ajustando Coordenadas

Após identificar o problema, edite o arquivo de configuração:

```json
{
  "players": [
    {
      "nickname": {
        "x": 21.07,  ← Posição X (0-100%)
        "y": 20.80,  ← Posição Y (0-100%)
        "w": 10.56,  ← Largura (0-100%) - Aumente se texto está cortado
        "h": 5.88    ← Altura (0-100%)
      }
    }
  ]
}
```

### Dica: Use um editor de imagem

1. Abra a imagem original no Paint/GIMP/Photoshop
2. Use a ferramenta de seleção retangular
3. Anote as coordenadas e dimensões em pixels
4. Converta para porcentagem: `(valor / tamanho_total) * 100`

Exemplo:
- Imagem: 2400x1080
- Região do nickname: X=506, Y=225, W=253, H=63
- Percentuais: X=21.08%, Y=20.83%, W=10.54%, H=5.83%

## Limpeza Periódica

A pasta `debug/` cresce rapidamente. Para manter apenas os mais recentes:

**Windows (PowerShell)**:
```powershell
# Manter apenas arquivos dos últimos 7 dias
Get-ChildItem debug -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item
```

**Linux/Mac**:
```bash
# Manter apenas arquivos dos últimos 7 dias
find debug -type f -mtime +7 -delete
```

## Interpretando Nomenclatura

```
20260201_143052_009_screenshot1_nickname_processed.png
│      │    │    │       │         │         │
│      │    │    │       │         │         └─ Tipo de processamento
│      │    │    │       │         └─────────── Campo/região extraída
│      │    │    │       └───────────────────── Nome da imagem original
│      │    │    └───────────────────────────── Contador sequencial
│      │    └────────────────────────────────── Hora (HH:MM:SS)
│      └─────────────────────────────────────── Data (YYYY-MM-DD)
└────────────────────────────────────────────── Padrão fixo
```

Essa nomenclatura permite:
- Ordenar cronologicamente (começa com data/hora)
- Agrupar por imagem processada (nome da imagem)
- Identificar rapidamente o campo (nickname, stats, etc.)
- Distinguir processamentos diferentes (raw, processed, inverted)

## Ferramentas Recomendadas

Para análise visual dos arquivos de debug:

- **Windows**: Windows Photo Viewer, IrfanView
- **Linux**: Eye of GNOME (eog), gThumb
- **Mac**: Preview, Xee³
- **Multiplataforma**: GIMP, ImageMagick (linha de comando)

Para comparação lado a lado:
```bash
# Linux/Mac com ImageMagick
montage debug/*_nickname_*.png -geometry +2+2 -tile 2x nicknames_comparison.png
```
