#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Busca de Texto em Páginas Web
Permite buscar texto específico na estrutura HTML de qualquer página web
"""
import requests
from bs4 import BeautifulSoup
import sys
import re
from urllib.parse import urlparse
from colorama import Fore, Style, init

# Inicializar colorama para Windows
init(autoreset=True)

class TextSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def solicitar_inputs(self):
        """Solicita URL e texto de busca do usuário"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}    BUSCADOR DE TEXTO EM PÁGINAS WEB")
        print(f"{Fore.CYAN}{'='*60}")
        print()
        
        # Solicitar URL
        while True:
            url = input(f"{Fore.YELLOW}Digite a URL da página: {Style.RESET_ALL}").strip()
            if self.validar_url(url):
                break
            print(f"{Fore.RED}❌ URL inválida! Tente novamente.{Style.RESET_ALL}")
        
        # Solicitar texto de busca
        texto_busca = input(f"{Fore.YELLOW}Digite o texto a ser buscado: {Style.RESET_ALL}").strip()
        
        # Opções de busca
        print(f"\n{Fore.MAGENTA}Opções de busca:")
        print(f"{Fore.WHITE}1. Case sensitive (diferencia maiúsculas/minúsculas)")
        print(f"{Fore.WHITE}2. Case insensitive (não diferencia maiúsculas/minúsculas)")
        
        opcao = input(f"{Fore.YELLOW}Escolha uma opção (1 ou 2, padrão=2): {Style.RESET_ALL}").strip()
        case_sensitive = opcao == "1"
        
        return url, texto_busca, case_sensitive
    
    def validar_url(self, url):
        """Valida se a URL está no formato correto"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def obter_pagina(self, url):
        """Faz a requisição HTTP e retorna o conteúdo da página"""
        try:
            print(f"\n{Fore.BLUE}🌐 Acessando a página...")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Verificar se é HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'html' not in content_type:
                print(f"{Fore.RED}⚠️  Aviso: Esta página pode não ser HTML puro.")
            
            # Verificar se é uma página dinâmica/SPA
            self.verificar_pagina_dinamica(response.text, url)
            
            print(f"{Fore.GREEN}✅ Página carregada com sucesso!")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Erro ao acessar a página: {e}")
            return None
    
    def buscar_texto_na_pagina(self, html_content, texto_busca, case_sensitive=False):
        """Busca o texto na estrutura HTML e retorna os resultados"""
        print(f"\n{Fore.BLUE}🔍 Analisando estrutura HTML...")
        
        # Dividir HTML em linhas para análise
        linhas_html = html_content.splitlines()
        resultados = []
        
        # Configurar padrão de busca
        flags = 0 if case_sensitive else re.IGNORECASE
        padrao = re.escape(texto_busca)
        
        # Buscar em cada linha
        for num_linha, linha in enumerate(linhas_html, 1):
            if re.search(padrao, linha, flags):
                # Extrair contexto e elemento HTML
                contexto = self.extrair_contexto(linha, texto_busca, case_sensitive)
                elemento = self.identificar_elemento_html(linha)
                
                resultados.append({
                    'linha': num_linha,
                    'conteudo_linha': linha.strip(),
                    'contexto': contexto,
                    'elemento': elemento
                })
        
        # Também buscar no texto visível da página
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            texto_visivel = soup.get_text()
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Aviso: Erro ao processar HTML para texto visível: {e}")
            texto_visivel = ""
        
        return resultados, self.contar_ocorrencias_visiveis(texto_visivel, texto_busca, case_sensitive)
    
    def extrair_contexto(self, linha, texto_busca, case_sensitive):
        """Extrai o contexto ao redor do texto encontrado"""
        flags = 0 if case_sensitive else re.IGNORECASE
        
        # Encontrar todas as ocorrências na linha
        matches = list(re.finditer(re.escape(texto_busca), linha, flags))
        contextos = []
        
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(linha), match.end() + 30)
            contexto = linha[start:end]
            
            # Destacar o texto encontrado
            if case_sensitive:
                contexto_destacado = contexto.replace(texto_busca, f">>>{texto_busca}<<<")
            else:
                # Para case insensitive, precisamos destacar a ocorrência exata
                texto_real = linha[match.start():match.end()]
                contexto_destacado = contexto.replace(texto_real, f">>>{texto_real}<<<")
            
            contextos.append(contexto_destacado)
        
        return contextos
    
    def identificar_elemento_html(self, linha):
        """Identifica o tipo de elemento HTML da linha"""
        linha_limpa = linha.strip()
        
        # Padrões de elementos HTML
        if re.match(r'<h[1-6]', linha_limpa, re.IGNORECASE):
            return "Cabeçalho"
        elif re.match(r'<p\b', linha_limpa, re.IGNORECASE):
            return "Parágrafo"
        elif re.match(r'<a\b', linha_limpa, re.IGNORECASE):
            return "Link"
        elif re.match(r'<div\b', linha_limpa, re.IGNORECASE):
            return "Div"
        elif re.match(r'<span\b', linha_limpa, re.IGNORECASE):
            return "Span"
        elif re.match(r'<title\b', linha_limpa, re.IGNORECASE):
            return "Título da Página"
        elif re.match(r'<meta\b', linha_limpa, re.IGNORECASE):
            return "Meta Tag"
        elif re.match(r'<img\b', linha_limpa, re.IGNORECASE):
            return "Imagem"
        elif re.match(r'<script\b', linha_limpa, re.IGNORECASE):
            return "Script"
        elif re.match(r'<style\b', linha_limpa, re.IGNORECASE):
            return "CSS/Style"
        elif re.match(r'<.*?>', linha_limpa):
            return "Outro HTML"
        else:
            return "Texto/Conteúdo"
    
    def contar_ocorrencias_visiveis(self, texto_visivel, texto_busca, case_sensitive):
        """Conta ocorrências no texto visível da página"""
        if case_sensitive:
            return texto_visivel.count(texto_busca)
        else:
            return texto_visivel.lower().count(texto_busca.lower())
    
    def exibir_resultados(self, resultados, texto_busca, ocorrencias_visiveis, url):
        """Exibe os resultados da busca de forma formatada"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}                     RESULTADOS DA BUSCA")
        print(f"{Fore.CYAN}{'='*80}")
        
        print(f"{Fore.WHITE}URL analisada: {Fore.YELLOW}{url}")
        print(f"{Fore.WHITE}Texto buscado: {Fore.YELLOW}'{texto_busca}'")
        print(f"{Fore.WHITE}Ocorrências na estrutura HTML: {Fore.GREEN}{len(resultados)}")
        print(f"{Fore.WHITE}Ocorrências no texto visível: {Fore.GREEN}{ocorrencias_visiveis}")
        
        if not resultados:
            print(f"\n{Fore.RED}❌ Nenhuma ocorrência encontrada na estrutura HTML.")
            if ocorrencias_visiveis > 0:
                print(f"{Fore.YELLOW}💡 Porém, o texto foi encontrado {ocorrencias_visiveis} vez(es) no conteúdo visível da página.")
            return
        
        print(f"\n{Fore.CYAN}📍 DETALHES DAS OCORRÊNCIAS:")
        print(f"{Fore.CYAN}{'-'*80}")
        
        for i, resultado in enumerate(resultados, 1):
            print(f"\n{Fore.YELLOW}[{i}] Linha {resultado['linha']} - {resultado['elemento']}")
            print(f"{Fore.WHITE}Código HTML:")
            print(f"{Fore.LIGHTBLACK_EX}   {resultado['conteudo_linha'][:100]}...")
            
            print(f"{Fore.WHITE}Contexto(s):")
            for j, contexto in enumerate(resultado['contexto']):
                print(f"{Fore.LIGHTGREEN_EX}   {j+1}. {contexto}")
        
        # Resumo por tipo de elemento
        self.exibir_resumo_elementos(resultados)
    
    def exibir_resumo_elementos(self, resultados):
        """Exibe um resumo agrupado por tipo de elemento"""
        elementos = {}
        for resultado in resultados:
            elemento = resultado['elemento']
            if elemento not in elementos:
                elementos[elemento] = 0
            elementos[elemento] += len(resultado['contexto'])
        
        print(f"\n{Fore.CYAN}📊 RESUMO POR TIPO DE ELEMENTO:")
        print(f"{Fore.CYAN}{'-'*40}")
        
        for elemento, count in sorted(elementos.items(), key=lambda x: x[1], reverse=True):
            print(f"{Fore.WHITE}{elemento}: {Fore.GREEN}{count} ocorrência(s)")
    
    def executar(self):
        """Método principal que executa o script"""
        try:
            # Solicitar inputs do usuário
            url, texto_busca, case_sensitive = self.solicitar_inputs()
            
            # Obter conteúdo da página
            html_content = self.obter_pagina(url)
            if not html_content:
                return
            
            # Buscar texto na página
            resultados, ocorrencias_visiveis = self.buscar_texto_na_pagina(
                html_content, texto_busca, case_sensitive
            )
            
            # Exibir resultados
            self.exibir_resultados(resultados, texto_busca, ocorrencias_visiveis, url)
            
            # Perguntar se quer salvar resultados
            if resultados:
                self.salvar_resultados_opcao(resultados, texto_busca, url)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Operação cancelada pelo usuário.")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Erro inesperado: {e}")
    
    def salvar_resultados_opcao(self, resultados, texto_busca, url):
        """Pergunta se o usuário quer salvar os resultados"""
        # Calcular tamanho estimado do arquivo
        tamanho_bytes = self.calcular_tamanho_arquivo_resultado(resultados, texto_busca, url)
        tamanho_formatado = self.formatar_tamanho_arquivo(tamanho_bytes)
        
        print(f"\n{Fore.MAGENTA}💾 Deseja salvar os resultados em um arquivo?")
        print(f"{Fore.CYAN}   Tamanho estimado do arquivo: {Fore.YELLOW}{tamanho_formatado}")
        print(f"{Fore.MAGENTA}   (s/n): ", end="")
        
        if input().strip().lower() in ['s', 'sim', 'y', 'yes']:
            self.salvar_resultados(resultados, texto_busca, url)
    
    def salvar_resultados(self, resultados, texto_busca, url):
        """Salva os resultados em um arquivo de texto"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"busca_resultado_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"RESULTADO DA BUSCA DE TEXTO\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"URL: {url}\n")
                f.write(f"Texto buscado: '{texto_busca}'\n")
                f.write(f"Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de ocorrências: {len(resultados)}\n\n")
                
                for i, resultado in enumerate(resultados, 1):
                    f.write(f"[{i}] Linha {resultado['linha']} - {resultado['elemento']}\n")
                    f.write(f"HTML: {resultado['conteudo_linha']}\n")
                    f.write(f"Contexto(s):\n")
                    for j, contexto in enumerate(resultado['contexto']):
                        f.write(f"  {j+1}. {contexto}\n")
                    f.write("\n" + "-"*50 + "\n\n")
            
            print(f"{Fore.GREEN}✅ Resultados salvos em: {filename}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao salvar arquivo: {e}")
    
    def verificar_pagina_dinamica(self, html_content, url):
        """Verifica se a página é dinâmica/SPA e exibe aviso"""
        indicadores_dinamicos = [
            'react', 'angular', 'vue.js', 'next.js', 'nuxt',
            'app.js', 'bundle.js', 'main.js', 'runtime.js',
            'data-reactroot', 'ng-app', 'v-app', '__NEXT_DATA__',
            'spa-', 'single-page', 'clientside'
        ]
        
        # Sites conhecidos que são dinâmicos
        sites_dinamicos = [
            'ss.com', 'instagram.com', 'facebook.com', 
            'twitter.com', 'x.com', 'linkedin.com', 'tiktok.com',
            'netflix.com', 'spotify.com', 'discord.com'
        ]
        
        html_lower = html_content.lower()
        url_lower = url.lower()
        
        # Verificar se é um site conhecido como dinâmico
        for site in sites_dinamicos:
            if site in url_lower:
                print(f"{Fore.YELLOW}⚠️  AVISO: Esta página ({site}) é conhecida por ser dinâmica.")
                print(f"{Fore.YELLOW}   O conteúdo pode ser carregado via JavaScript após o carregamento inicial.")
                print(f"{Fore.YELLOW}   Os resultados podem não refletir todo o conteúdo visível ao usuário.")
                return
        
        # Verificar indicadores de páginas dinâmicas no HTML
        indicadores_encontrados = []
        for indicador in indicadores_dinamicos:
            if indicador in html_lower:
                indicadores_encontrados.append(indicador)
        
        if indicadores_encontrados:
            print(f"{Fore.YELLOW}⚠️  AVISO: Esta página parece ser dinâmica/SPA.")
            print(f"{Fore.YELLOW}   Indicadores encontrados: {', '.join(indicadores_encontrados[:3])}...")
            print(f"{Fore.YELLOW}   O conteúdo pode ser carregado via JavaScript após o carregamento inicial.")
            print(f"{Fore.YELLOW}   Para páginas como esta, considere usar ferramentas específicas de scraping como Selenium, Playwright ou Puppeteer")
    
    def calcular_tamanho_arquivo_resultado(self, resultados, texto_busca, url):
        """Calcula o tamanho estimado do arquivo de resultado"""
        import datetime
        
        # Simular o conteúdo que seria escrito
        conteudo_simulado = f"RESULTADO DA BUSCA DE TEXTO\n"
        conteudo_simulado += f"{'='*50}\n\n"
        conteudo_simulado += f"URL: {url}\n"
        conteudo_simulado += f"Texto buscado: '{texto_busca}'\n"
        conteudo_simulado += f"Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        conteudo_simulado += f"Total de ocorrências: {len(resultados)}\n\n"
        
        for i, resultado in enumerate(resultados, 1):
            conteudo_simulado += f"[{i}] Linha {resultado['linha']} - {resultado['elemento']}\n"
            conteudo_simulado += f"HTML: {resultado['conteudo_linha']}\n"
            conteudo_simulado += f"Contexto(s):\n"
            for j, contexto in enumerate(resultado['contexto']):
                conteudo_simulado += f"  {j+1}. {contexto}\n"
            conteudo_simulado += "\n" + "-"*50 + "\n\n"
        
        # Calcular tamanho em bytes (UTF-8)
        tamanho_bytes = len(conteudo_simulado.encode('utf-8'))
        
        return tamanho_bytes
    
    def formatar_tamanho_arquivo(self, tamanho_bytes):
        """Formata o tamanho do arquivo em uma unidade legível"""
        if tamanho_bytes < 1024:
            return f"{tamanho_bytes} bytes"
        elif tamanho_bytes < 1024 * 1024:
            return f"{tamanho_bytes / 1024:.1f} KB"
        elif tamanho_bytes < 1024 * 1024 * 1024:
            return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{tamanho_bytes / (1024 * 1024 * 1024):.1f} GB"


def main():
    """Função principal"""
    searcher = TextSearcher()
    searcher.executar()


if __name__ == "__main__":
    main()
