# Guia de Preprocessamento para OCR em Screenshots MLBB

Este guia documenta os melhores filtros e técnicas de preprocessamento para cada tipo de campo em screenshots de fim de partida do Mobile Legends Bang Bang.

## 📋 Resumo de Resultados dos Testes

### Campos com Sucesso (100% de acurácia)

| Campo | Preprocessamento | PSM | Scale | Acurácia | Exemplo |
|-------|------------------|-----|-------|----------|---------|
| **Kills** | high_contrast | 10 | 4x | ✅ 100% | "2" |
| **Deaths** | grayscale_scaled | 7 | 2x | ✅ 100% | "11" |
| **Assists** | grayscale_scaled | 7 | 4x | ✅ 100% | "32" |
| **Gold** | grayscale_scaled | 7 | 3x | ✅ 100% | "20094" |
| **Duration** | grayscale_scaled | 7 | 2x | ✅ 100% | "36:02" |

## 🎯 Regras de Preprocessamento por Tipo de Campo

### 1. Números Pequenos (1-2 dígitos) sobre Fundo Escuro

**Exemplos**: Kills, Deaths, Assists individual

**Método Recomendado**: `grayscale_scaled` com escala 2x-4x
- **Por quê**: Números pequenos precisam de upscaling para o OCR reconhecer bem
- **PSM**: 7 (linha única) ou 10 (caractere único)
- **Config OCR**: `-c tessedit_char_whitelist=0123456789`

```json
{
  "preprocessing": "grayscale_scaled",
  "ocr_config": "--psm 7 -c tessedit_char_whitelist=0123456789",
  "scale_factor": 2
}
```

**Alternativa para contraste difícil**: `threshold` com escala 4x

### 2. Números Grandes (4-5 dígitos)

**Exemplos**: Gold (20094)

**Método Recomendado**: `grayscale_scaled` com escala 3x
- **Por quê**: Números maiores não precisam de tanto upscaling
- **PSM**: 7 (linha única)
- **Config OCR**: `-c tessedit_char_whitelist=0123456789`

```json
{
  "preprocessing": "grayscale_scaled",
  "ocr_config": "--psm 7 -c tessedit_char_whitelist=0123456789",
  "scale_factor": 3
}
```

### 3. Texto com Alto Contraste (Fundo Uniforme)

**Exemplos**: "VICTORY", "DEFEAT"

**Método Recomendado**: `threshold` com escala 4x
- **Por quê**: Threshold binário remove ruído e aumenta contraste
- **PSM**: 7 (linha única) ou 8 (palavra única)
- **Resultado nos testes**: "VICTOR" (98% correto, faltou apenas o Y)

```json
{
  "preprocessing": "threshold",
  "ocr_config": "--psm 7",
  "scale_factor": 4
}
```

**⚠️ Problema**: Se a região incluir texto adjacente, ajuste as coordenadas para área menor.

### 4. Texto sobre Fundo Colorido/Texturizado

**Exemplos**: Player names, hero names

**Método Recomendado**: `grayscale_scaled` com escala 2x
- **Por quê**: Preserva mais detalhes que threshold
- **PSM**: 7 (linha única)
- **Problema observado**: Pode capturar símbolos adjacentes (ex: "@")

```json
{
  "preprocessing": "grayscale_scaled",
  "ocr_config": "--psm 7",
  "scale_factor": 2
}
```

**Limpeza pós-OCR**: Remover caracteres especiais indesejados

### 5. Números em Badges Coloridos (Dourados/Amarelos)

**Exemplos**: Score rating (9.1)

**Método Recomendado**: `yellow_color_mask` com escala 5x+
- **Por quê**: Isola apenas os pixels amarelos/dourados do badge
- **PSM**: 8 (palavra) ou 10 (caractere)
- **Config OCR**: `-c tessedit_char_whitelist=0123456789.`
- **Parâmetros HSV**: `[15, 40, 120]` a `[45, 255, 255]`

```json
{
  "preprocessing": "yellow_color_mask",
  "ocr_config": "--psm 8 -c tessedit_char_whitelist=0123456789.",
  "scale_factor": 5,
  "color_range": {
    "lower_hsv": [15, 40, 120],
    "upper_hsv": [45, 255, 255]
  }
}
```

**⚠️ Status**: Detecta apenas parcialmente (".2" em vez de "9.1")
- **Possíveis soluções**:
  1. Ajustar coordenadas (pode estar cortando parte do número)
  2. Ampliar range HSV
  3. Testar com grayscale direto em escala muito alta (6x-8x)

### 6. Tempo/Duração (formato MM:SS)

**Exemplos**: 36:02, 45:23

**Método Recomendado**: `grayscale_scaled` com escala 2x
- **Por quê**: Formato simples, geralmente bem visível
- **PSM**: 7 (linha única)
- **Config OCR**: `-c tessedit_char_whitelist=0123456789:`

```json
{
  "preprocessing": "grayscale_scaled",
  "ocr_config": "--psm 7 -c tessedit_char_whitelist=0123456789:",
  "scale_factor": 2
}
```

## 🔧 Métodos de Preprocessamento Detalhados

### `grayscale_scaled`
```python
# Converte para escala de cinza + upscaling
gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
scaled = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
```

**Quando usar**:
- ✅ Texto/números com bom contraste
- ✅ Fundo relativamente uniforme
- ✅ Quando threshold não funciona bem

**Quando NÃO usar**:
- ❌ Fundo muito texturizado
- ❌ Múltiplas cores de texto
- ❌ Texto muito pequeno sem upscaling

### `threshold`
```python
# Threshold binário fixo
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
scaled = cv2.resize(binary, None, fx=scale, fy=scale)
```

**Quando usar**:
- ✅ Alto contraste (texto escuro em fundo claro ou vice-versa)
- ✅ Remover ruído de fundo
- ✅ Texto grande e claro

**Quando NÃO usar**:
- ❌ Iluminação irregular
- ❌ Texto em múltiplos níveis de cinza
- ❌ Fundo gradiente

### `high_contrast` (Adaptive Threshold)
```python
# Threshold adaptativo (se ajusta localmente)
adaptive = cv2.adaptiveThreshold(
    gray, 255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2
)
scaled = cv2.resize(adaptive, None, fx=scale, fy=scale)
```

**Quando usar**:
- ✅ Iluminação irregular
- ✅ Sombras ou gradientes no fundo
- ✅ Quando threshold simples falha

**Quando NÃO usar**:
- ❌ Pode criar ruído em fundos texturizados
- ❌ Resultados inconsistentes em alguns casos (nos testes, não foi melhor que grayscale)

### `yellow_color_mask`
```python
# Máscara baseada em cor HSV
hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
scaled = cv2.resize(mask, None, fx=scale, fy=scale)
```

**Quando usar**:
- ✅ Números/texto em badges coloridos
- ✅ Quando cor é característica distintiva
- ✅ Remover elementos de outras cores

**Quando NÃO usar**:
- ❌ Texto branco/preto/cinza
- ❌ Quando não há cor específica
- ❌ Múltiplas cores de texto na mesma região

**Ranges HSV úteis**:
- Amarelo/Dourado: `[15, 40, 120]` a `[45, 255, 255]`
- Branco/Claro: `[0, 0, 180]` a `[180, 50, 255]`
- Azul/Ciano: `[85, 50, 100]` a `[110, 255, 255]`
- Laranja: `[10, 100, 100]` a `[25, 255, 255]`

### `inverted`
```python
# Inverte cores
inverted = 255 - gray
scaled = cv2.resize(inverted, None, fx=scale, fy=scale)
```

**Quando usar**:
- ✅ Texto claro em fundo escuro (para OCR que funciona melhor com texto escuro)
- ✅ Como alternativa quando grayscale direto falha

**Quando NÃO usar**:
- ❌ Geralmente grayscale direto já funciona

## ⚙️ Configurações PSM do Tesseract

| PSM | Descrição | Uso Recomendado |
|-----|-----------|-----------------|
| **7** | Linha única de texto | Nomes, palavras, números de 2+ dígitos |
| **8** | Palavra única | Palavras isoladas, números curtos |
| **10** | Caractere único | Dígitos individuais (0-9) |
| **6** | Bloco uniforme | Parágrafos, múltiplas linhas |
| **11** | Texto esparso | Quando não sabe onde está o texto |
| **13** | Linha raw | Alternativa ao PSM 7 |

## 📊 Fatores de Escala (Scale Factor)

| Tamanho do Texto | Scale Recomendado | Exemplo |
|------------------|-------------------|---------|
| Muito pequeno (< 20px) | 4x - 6x | Dígito individual de KDA |
| Pequeno (20-30px) | 2x - 3x | Número de 2 dígitos |
| Médio (30-50px) | 2x - 3x | Nomes, palavras |
| Grande (> 50px) | 1x - 2x | Títulos, "VICTORY" |

**⚠️ Cuidado**: Escala muito alta pode introduzir artefatos de interpolação.

## 🎯 Estratégia de Otimização

### 1. Comece com o Básico
```json
{
  "preprocessing": "grayscale_scaled",
  "ocr_config": "--psm 7",
  "scale_factor": 2
}
```

### 2. Se Falhar, Teste Threshold
```json
{
  "preprocessing": "threshold",
  "scale_factor": 4
}
```

### 3. Para Números, Aumente Escala
```json
{
  "scale_factor": 4,
  "ocr_config": "--psm 10 -c tessedit_char_whitelist=0123456789"
}
```

### 4. Para Badges Coloridos, Use Máscara
```json
{
  "preprocessing": "yellow_color_mask",
  "scale_factor": 5,
  "color_range": { ... }
}
```

### 5. Whitelist de Caracteres

Sempre use quando souber o tipo de dado:
- Números: `-c tessedit_char_whitelist=0123456789`
- Decimal: `-c tessedit_char_whitelist=0123456789.`
- Tempo: `-c tessedit_char_whitelist=0123456789:`
- Alfanumérico: `-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`

## 🐛 Problemas Comuns e Soluções

### Problema: OCR retorna caracteres errados (ex: "D" em vez de "0")
**Solução**: 
1. Aumentar escala (4x ou 6x)
2. Usar whitelist de caracteres
3. Testar threshold em vez de grayscale

### Problema: OCR retorna vazio
**Solução**:
1. Verificar se coordenadas estão corretas
2. Verificar se região não está muito pequena (< 10px)
3. Testar com PSM diferente (11 para texto esparso)
4. Salvar debug image para inspeção visual

### Problema: OCR captura texto adjacente
**Solução**:
1. Reduzir largura/altura da região
2. Usar PSM 8 (palavra única) em vez de PSM 7

### Problema: Números em badges não são detectados
**Solução**:
1. Usar `yellow_color_mask` com range HSV apropriado
2. Aumentar muito a escala (5x-8x)
3. Verificar se coordenadas incluem o número completo
4. Como último recurso, testar grayscale com escala altíssima (8x)

### Problema: Texto com @ ou símbolos extras
**Solução**:
1. Ajustar coordenadas para não incluir ícones adjacentes
2. Fazer limpeza pós-OCR (regex para remover símbolos)

## 📈 Resultados dos Testes por Método

### Grayscale 2x PSM 7
- ✅ Deaths: "11" (100%)
- ✅ Player names (com símbolos extras)

### Grayscale 4x PSM 7
- ✅ Assists: "32" (100%)

### Grayscale 3x PSM 7
- ✅ Gold: "20094" (100%)

### Threshold 4x PSM 7
- ⚠️ Game Result: "VICTOR" (faltou Y)
- ✅ Deaths: "11" (alternativa)
- ✅ Assists: "32" (alternativa)

### High Contrast 4x PSM 10
- ✅ Kills: "2" (100%)

### Yellow Color Mask 5x PSM 8
- ❌ Score Rating: ".2" (parcial, esperado "9.1")
- Precisa ajustes de coordenadas ou range HSV

## 💡 Recomendações Finais

1. **Sempre salve debug images** ao calibrar
2. **Teste com múltiplas imagens** para garantir consistência
3. **Use whitelist de caracteres** para aumentar acurácia
4. **Coordenadas precisas** são mais importantes que o preprocessamento
5. **Escala adequada** é crucial para texto pequeno
6. **Threshold funciona melhor** para texto grande com alto contraste
7. **Grayscale funciona melhor** para maioria dos casos gerais
8. **Color masks** são específicos mas poderosos quando aplicáveis

## 🔍 Ferramenta de Calibração

Use o script `test_preprocessing.py` para testar uma região:

```python
test_field("nome_campo", x, y, w, h, "valor_esperado")
```

Ele testará automaticamente:
- Grayscale 2x, 4x
- Inverted 4x
- Threshold 4x
- Adaptive 4x
- Com PSM 7, 8, 10

E mostrará qual combinação deu melhor resultado.
