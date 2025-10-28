import requests
import json
import datetime
import time
import os
import winsound
from urllib.parse import quote

class PriceAlertTracker:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.load_config()
        
    def load_config(self):
        """Carrega toda a configuração do JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.crypto_mapping = config.get("crypto_mapping", {})
            self.assets = config.get("assets", [])
            self.settings = config.get("settings", {})
            
            print(f"✅ Configuração carregada: {len(self.assets)} ativos")
            print(f"✅ Mapeamento: {len(self.crypto_mapping)} criptomoedas")
            
        except FileNotFoundError:
            print(f"❌ Arquivo {self.config_file} não encontrado!")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Erro no JSON: {e}")
            raise
    
    def get_crypto_price(self, symbol: str) -> float:
        """Obtém preço de criptomoeda - CORRIGIDO"""
        try:
            coin_id = self.crypto_mapping.get(symbol.upper())
            if not coin_id:
                print(f"❌ {symbol} não encontrado no mapeamento")
                return 0
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Erro HTTP {response.status_code} na API")
                return 0
                
            data = response.json()
            
            if coin_id in data and "usd" in data[coin_id]:
                price = data[coin_id]["usd"]
                print(f"   ✅ Preço obtido: ${price:.2f}")
                return price
            else:
                print(f"❌ Dados inválidos da API para {symbol}")
                return 0
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout ao buscar {symbol}")
            return 0
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão ao buscar {symbol}")
            return 0
        except Exception as e:
            print(f"❌ Erro inesperado com {symbol}: {e}")
            return 0
    
    def get_stock_price(self, symbol: str) -> float:
        """Obtém preço de ação - CORRIGIDO"""
        try:
            # Limpa e formata o símbolo para a URL
            clean_symbol = symbol.strip().upper()
            
            # Yahoo Finance API alternativa
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean_symbol}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Erro HTTP {response.status_code} para {clean_symbol}")
                return 0
            
            data = response.json()
            
            # Verifica se a estrutura de dados está correta
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                if "meta" in result and "regularMarketPrice" in result["meta"]:
                    price = result["meta"]["regularMarketPrice"]
                    print(f"   ✅ Preço obtido: ${price:.2f}")
                    return price
            
            print(f"❌ Estrutura de dados inválida para {clean_symbol}")
            return 0
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout ao buscar ação {symbol}")
            return 0
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão ao buscar {symbol}")
            return 0
        except Exception as e:
            print(f"❌ Erro ao buscar ação {symbol}: {e}")
            return 0
    
    def play_alert_sound(self):
        """Toca alerta sonoro"""
        try:
            winsound.Beep(1000, 1000)
            time.sleep(0.3)
            winsound.Beep(1200, 800)
        except:
            print("🔊 Alerta sonoro!")
    
    def check_alerts(self):
        """Verifica todos os ativos em busca de alertas"""
        print(f"\n📊 Verificando preços - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        alerts_triggered = []
        successful_checks = 0
        
        for asset in self.assets:
            print(f"\n🔍 Verificando {asset['symbol']} ({asset['name']})...")
            
            current_price = self.get_current_price(asset)
            
            if current_price > 0:
                successful_checks += 1
                self.print_asset_status(asset, current_price)
                
                if current_price >= asset["alert_price"]:
                    alert_data = self.trigger_alert(asset, current_price)
                    alerts_triggered.append(alert_data)
            else:
                print(f"   ⚠️  Não foi possível obter preço para {asset['symbol']}")
        
        print(f"\n📈 Resumo: {successful_checks}/{len(self.assets)} ativos verificados")
        
        if alerts_triggered:
            self.save_alerts_to_log(alerts_triggered)
        
        return alerts_triggered
    
    def get_current_price(self, asset: dict) -> float:
        """Obtém preço atual baseado no tipo do ativo"""
        if asset["type"] == "crypto":
            return self.get_crypto_price(asset["symbol"])
        else:
            return self.get_stock_price(asset["symbol"])
    
    def print_asset_status(self, asset: dict, current_price: float):
        """Mostra status do ativo"""
        status = "🚨 ALERTA ATINGIDO!" if current_price >= asset["alert_price"] else "⏳ Aguardando..."
        print(f"   {status}")
        print(f"   Preço atual: ${current_price:.2f}")
        print(f"   Alerta: ${asset['alert_price']:.2f}")
        
        if current_price < asset["alert_price"]:
            difference = asset["alert_price"] - current_price
            percent_to_go = (difference / current_price) * 100
            print(f"   Faltam ${difference:.2f} ({percent_to_go:.1f}%)")
        else:
            profit = current_price - asset["alert_price"]
            print(f"   ✅ Acima do alvo por ${profit:.2f}")
    
    def trigger_alert(self, asset: dict, current_price: float) -> dict:
        """Dispara alerta para um ativo"""
        alert_msg = f"🚨 ALERTA! {asset['symbol']} atingiu ${current_price:.2f}"
        print(f"   💥 {alert_msg}")
        
        if self.settings.get("play_sound_alert", True):
            self.play_alert_sound()
        
        return {
            "symbol": asset["symbol"],
            "name": asset["name"],
            "type": asset["type"],
            "current_price": current_price,
            "alert_price": asset["alert_price"],
            "timestamp": datetime.datetime.now().isoformat(),
            "buy_date": asset.get("buy_date", ""),
            "buy_price": asset.get("buy_price", 0)
        }
    
    def save_alerts_to_log(self, alerts: list):
        """Salva alertas no arquivo de log"""
        log_file = "alert_log.json"
        
        try:
            # Carrega alertas existentes
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_alerts = json.load(f)
            else:
                existing_alerts = []
            
            # Adiciona apenas alertas novos do dia
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            new_alerts = 0
            
            for alert in alerts:
                alert_date = alert["timestamp"][:10]
                
                # Verifica se já existe alerta igual hoje
                existing_today = any(
                    a["symbol"] == alert["symbol"] and a["timestamp"][:10] == alert_date
                    for a in existing_alerts
                )
                
                if not existing_today:
                    existing_alerts.append(alert)
                    new_alerts += 1
            
            # Salva arquivo atualizado
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_alerts, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {new_alerts} novo(s) alerta(s) salvos no log")
            
        except Exception as e:
            print(f"❌ Erro ao salvar log: {e}")
    
    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""
        print("\n🎯 Iniciando monitoramento contínuo...")
        print("📍 Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.check_alerts()
                
                interval = self.settings.get("check_interval_minutes", 60)
                next_check = datetime.datetime.now() + datetime.timedelta(minutes=interval)
                print(f"\n⏰ Próxima verificação: {next_check.strftime('%H:%M')}")
                print("-" * 50)
                time.sleep(interval * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento parado pelo usuário")

def main():
    print("💰 SISTEMA DE ALERTAS DE PREÇOS")
    print("=" * 40)
    
    tracker = PriceAlertTracker()
    
    # Verificação única
    alerts = tracker.check_alerts()
    
    if alerts:
        print(f"\n🎯 {len(alerts)} ALERTA(S) DISPARADOS!")
    else:
        print(f"\n✅ Nenhum alerta disparado")
    
    # Monitoramento contínuo
    response = input("\n🔄 Iniciar monitoramento contínuo? (s/n): ").strip().lower()
    if response in ['s', 'sim', 'y', 'yes']:
        tracker.run_continuous_monitoring()
    else:
        print("👋 Execução única concluída")

if __name__ == "__main__":
    main()