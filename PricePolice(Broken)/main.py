import smtplib
import schedule
import time
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

def enviar_notificacao(mensagem):
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    messagebox.showinfo("Notificação", mensagem)
    root.destroy()

def obter_preco(produto_url):
    try:
        response = requests.get(produto_url)
        response.raise_for_status()  # Levanta um erro para status HTTP ruim
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ajustar ao site específico
        preco_texto = soup.find('span', {'class': 'andes-money-amount__fraction'}).text
        preco = float(preco_texto.replace('R$', '').replace('.', '').replace(',', '.'))
        return preco
    except Exception as e:
        print(f"Erro ao obter o preço: {e}")
        return None

def monitorar_preco(produto_url, preco_alvo, produto):
    preco_atual = obter_preco(produto_url)
    
    if preco_atual is None:
        return  # Sai da função se o preço não pôde ser obtido

    if preco_atual <= preco_alvo:
        mensagem = (f"O produto {produto} que você está monitorando caiu de preço!\n"
                    f"O preço atual é: R${preco_atual:.2f}")
        enviar_notificacao(mensagem)
    else:
        print(f"O preço do produto não caiu ainda.\nO preço do produto é atualmente: R${preco_atual:.2f}")

if __name__ == '__main__':
    print("Iniciando monitoramento...")

    # INFO DO PRODUTO
    produto_url = 'https://lista.mercadolivre.com.br/terre-d%E2%80%99herm%C3%A8s-200ml#D[A:terre%20d%E2%80%99herm%C3%A8s%20200ml]'
    preco_alvo = 1000.0
    produto = 'Terre d Hermes 200ml'

    monitorar_preco(produto_url, preco_alvo, produto)
#como dar upgrade no pip
#python -m pip install --upgrade pip