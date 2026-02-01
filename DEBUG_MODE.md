# Modo Debug

O modo debug permite visualizar todas as imagens intermediárias usadas no processo de extração de dados. Isso é muito útil para:

- **Diagnosticar problemas** de extração de texto
- **Ajustar coordenadas** de regiões para diferentes resoluções
- **Verificar qualidade** do pré-processamento de imagem
- **Entender o processo** de OCR passo a passo

## Como Ativar

Adicione a flag `--debug` ao executar o comando:

```bash
# Extrair dados de um jogador específico com debug
python main.py -i screenshot.png -p "MTF7" --debug

# Extrair todos os jogadores com debug
python main.py -i screenshot.png --all-players --debug

# Processar múltiplas imagens com debug
python main.py -d ./screenshots --all-players --debug
```

## Saída do Modo Debug

Quando o modo debug está ativo, todas as imagens intermediárias são salvas na pasta `debug/` com nomenclatura detalhada:

### Estrutura dos Nomes de Arquivo

```
YYYYMMDD_HHMMSS_NNN_imagename_region_description.png
```

Onde:
- **YYYYMMDD_HHMMSS**: Data e hora da extração
- **NNN**: Contador sequencial (001, 002, 003...)
- **imagename**: Nome do arquivo de imagem original (sem extensão)
- **region**: Região/campo extraído (result, nickname, stats, etc.)
- **description**: Tipo de processamento aplicado (raw, processed, etc.)

### Exemplo de Arquivos Gerados

```
debug/
├── 20260201_143052_001_screenshot1_result_raw.png
├── 20260201_143052_002_result_processed.png
├── 20260201_143052_003_screenshot1_my_team_score_raw.png
├── 20260201_143052_004_my_team_score_processed.png
├── 20260201_143052_005_screenshot1_adversary_score_raw.png
├── 20260201_143052_006_adversary_score_processed.png
├── 20260201_143052_007_screenshot1_duration_raw.png
├── 20260201_143052_008_duration_processed.png
├── 20260201_143052_009_screenshot1_nickname_raw.png
├── 20260201_143052_010_nickname_processed.png
├── 20260201_143052_011_screenshot1_stats_raw.png
├── 20260201_143052_012_stats_processed_gray.png
├── 20260201_143052_013_stats_processed_inverted.png
├── 20260201_143052_014_screenshot1_ratio_raw.png
├── 20260201_143052_015_ratio_processed.png
├── 20260201_143052_016_ratio_yellow_mask.png
└── 20260201_143052_017_screenshot1_medal_raw.png
```

## Regiões Capturadas

### Informações da Partida

1. **result** (raw + processed)
   - Região que contém "VICTORY" ou "DEFEAT"
   - Processamento: threshold binário

2. **my_team_score** (raw + processed)
   - Placar do seu time
   - Processamento: escala de cinza + redimensionamento

3. **adversary_score** (raw + processed)
   - Placar do time adversário
   - Processamento: escala de cinza + redimensionamento

4. **duration** (raw + processed)
   - Duração da partida (formato mm:ss)
   - Processamento: escala de cinza + redimensionamento

### Dados do Jogador (Para cada jogador processado)

5. **nickname** (raw + processed)
   - Nome do jogador
   - Processamento: escala de cinza + redimensionamento

6. **stats** (raw + processed_gray + processed_inverted)
   - K/D/A e Gold (4 valores numéricos)
   - Múltiplos processamentos para melhor extração

7. **ratio** (raw + processed + yellow_mask)
   - Rating de performance
   - Processamento adicional para medalhas douradas

8. **medal** (raw)
   - Região da medalha (Gold/Silver/Bronze)
   - Detecção por cor, não OCR

## Dicas de Uso

### Para Diagnosticar Problemas de Extração

1. Execute com `--debug`
2. Abra as imagens na pasta `debug/`
3. Verifique se:
   - Os cortes estão corretos (arquivos `*_raw.png`)
   - O pré-processamento está adequado (arquivos `*_processed.png`)
   - O texto está legível nas imagens processadas

### Para Ajustar Coordenadas

Se os cortes não estiverem corretos:

1. Identifique qual região está incorreta nos arquivos `*_raw.png`
2. Edite o arquivo de configuração correspondente em `resolutions/`
3. Ajuste as coordenadas percentuais (x, y, w, h)
4. Execute novamente para verificar

### Para Otimizar Pré-processamento

Se o texto não está legível após processamento:

1. Examine os diferentes tipos de processamento aplicados
2. Considere ajustar parâmetros em `image_processor.py`
3. Teste diferentes métodos de pré-processamento

## Configuração Permanente

Para ativar o debug permanentemente em um arquivo de configuração:

```json
{
  "debug_mode": true,
  "debug_dir": "debug",
  "tesseract_cmd": null,
  "output_dir": "output",
  "active_profile": "default_2400x1080",
  "profiles": [...]
}
```

## Limpeza

A pasta `debug/` pode crescer rapidamente. Para limpar:

```bash
# Windows
rmdir /s /q debug

# Linux/Mac
rm -rf debug/
```

Ou manualmente, delete a pasta `debug/` quando não precisar mais das imagens.

## Performance

**Nota**: O modo debug pode reduzir a velocidade de processamento em cerca de 10-20% devido às operações adicionais de salvamento de imagem. Use apenas quando necessário para diagnóstico.
