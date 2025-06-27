import asciichartpy
import requests
import pygame
from pathlib import Path
import sys


class BitcoinTracker:
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    REFERENCE_PRICE = 106971  # Preço de referência (junho)
    
    def __init__(self, audio_dir=None):
        self.audio_dir = Path(audio_dir) if audio_dir else None
        self._setup_encoding()
    
    def _setup_encoding(self):
        """Configura encoding UTF-8 para output."""
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, Exception):
            pass
    
    def get_current_price(self):
        url = f"{self.BASE_URL}/simple/price?ids=bitcoin&vs_currencies=usd"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return int(response.json()['bitcoin']['usd'])
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"Erro ao obter preço atual: {e}")
            return None
    
    def get_historical_data(self, days=30):
        url = f"{self.BASE_URL}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [price[1] for price in data['prices']]
        except (requests.RequestException, KeyError) as e:
            print(f"Erro ao obter dados históricos: {e}")
            return []
    
    def display_price_info(self, current_price):
        print("\n" * 18)  # Limpa a tela
        print(f"Bitcoin vendido em junho por: ${self.REFERENCE_PRICE:,} USD\n")
        
        if current_price:
            print(f"Preço atual do Bitcoin (BTC): ${current_price:,} USD")
            
            # Calcula variação percentual
            variation = ((current_price - self.REFERENCE_PRICE) / self.REFERENCE_PRICE) * 100
            status = "📈" if variation > 0 else "📉"
            print(f"Variação desde junho: {status} {variation:+.2f}%")
        else:
            print("Não foi possível obter o preço atual.")
    
    def display_chart(self, historical_data):
        if not historical_data:
            print("Não foi possível gerar o gráfico - dados indisponíveis.")
            return
        
        print(f"\nGráfico do Bitcoin (últimos {len(historical_data)} dias):")
        try:
            chart = asciichartpy.plot(historical_data, {'height': 15})
            print(chart)
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
    
    def play_sound_alert(self, price):
        if not price or not self.audio_dir:
            return
        
        try:
            pygame.mixer.init()
            
            if price > 100000:
                audio_file = self.audio_dir / "waiting_sound.mp3"
                loops = 2
            elif price < 105000:
                audio_file = self.audio_dir / "cash_register.mp3"
                loops = 0
            else:
                return  # Sem som para preços intermediários
            
            if audio_file.exists():
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(loops)
                
                # Aguarda finalizar
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                print(f"Arquivo de áudio não encontrado: {audio_file}")
                
        except pygame.error as e:
            print(f"Erro no áudio: {e}")
        finally:
            try:
                pygame.mixer.quit()
            except:
                pass
    
    def run(self):
        current_price = self.get_current_price()
        
        self.display_price_info(current_price)
        
        historical_data = self.get_historical_data(30)
        self.display_chart(historical_data)
        
        if current_price:
            self.play_sound_alert(current_price)


def main():
    """Função principal."""
    # Configure o caminho para seus arquivos de áudio aqui (opcional)
    #audio_directory = r"C:\Users\jpger\Music"
    audio_directory = None
    
    tracker = BitcoinTracker(audio_directory)
    tracker.run()


if __name__ == "__main__":
    main()