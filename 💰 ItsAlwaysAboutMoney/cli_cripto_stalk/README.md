# Bitcoin Price Tracker 📈

Script Python simples para monitorar o preço do Bitcoin em tempo real com gráfico ASCII e alertas sonoros.

## Funcionalidades

- 💰 Preço atual do Bitcoin em USD
- 📊 Gráfico ASCII dos últimos 30 dias
- 📈 Cálculo de variação percentual
- 🔊 Alertas sonoros baseados no preço (opcional)

## Instalação

```bash
pip install requests asciichartpy pygame
```

## Uso Básico

```bash
python bitcoin_tracker.py
```

## Configuração de Áudio (Opcional)

Para habilitar alertas sonoros, edite o arquivo e configure o caminho dos áudios:

```python
# Na função main(), descomente e configure:
audio_directory = r"C:\caminho\para\seus\audios"
```

### Arquivos de áudio necessários:
- `waiting_sound.mp3` - Toca quando preço > $100,000
- `cash_register.mp3` - Toca quando preço < $105,000

## Exemplo de Saída

```
Bitcoin vendido em junho por: $106,971 USD

Preço atual do Bitcoin (BTC): $98,450 USD
Variação desde junho: 📉 -7.96%

Gráfico do Bitcoin (últimos 30 dias):
    98,450.00 ┤        ╭─╮
    95,230.00 ┤    ╭───╯ ╰╮
    92,010.00 ┤  ╭─╯      ╰─╮
    88,790.00 ┼──╯          ╰───
```

## API Utilizada

[CoinGecko API](https://www.coingecko.com/en/api) - Gratuita, sem necessidade de chave

## Requisitos

- Python 3.6+
- Conexão com internet
- Terminal com suporte UTF-8 (recomendado)